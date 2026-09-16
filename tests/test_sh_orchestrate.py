"""The loop's pure parts: round numbering, window pooling, the one-crown rule, and the upload's idempotence.
The stages that touch GitHub and the GPU are exercised by the real loop, not here."""

from __future__ import annotations

import json
from pathlib import Path

import sh.exports.upload as up
from sh.validator.orchestrate import Config, window_archive


def _cfg(tmp_path: Path, window: int = 8) -> Config:
    return Config(
        state=tmp_path / "state", repo=tmp_path / "repo", queue=tmp_path / "queue", pkg=tmp_path, window=window
    )


def test_only_ready_rounds_are_taken_from_the_queue_in_order(tmp_path):
    """A half-minted round has no READY marker and must never open."""
    from sh.validator.orchestrate import queue_ready

    cfg = _cfg(tmp_path)
    for rid, ready in (("r0004", True), ("r0003", True), ("r0005", False)):
        (cfg.queue / rid).mkdir(parents=True)
        if ready:
            (cfg.queue / rid / "READY").write_text("{}")
    assert queue_ready(cfg) == ["r0003", "r0004"]


def test_the_window_closes_on_the_clock(tmp_path):
    from sh.validator.orchestrate import window_state

    rd = tmp_path / "r0003"
    rd.mkdir()
    assert window_state(rd) == {"open": False, "remaining": 0}  # a legacy round has no window: nothing to wait for
    (rd / "window.json").write_text(json.dumps({"opens_at": 1000.0, "closes_at": 8200.0, "seconds": 7200}))
    assert window_state(rd, now=5000.0) == {"open": True, "remaining": 3200.0, "closes_at": 8200.0}
    assert window_state(rd, now=9000.0)["open"] is False


def _round_with_episode(cfg: Config, round_id: str) -> None:
    d = cfg.rounds / round_id / "episodes" / "null" / "t"
    d.mkdir(parents=True)
    (d / "episode.json").write_text(json.dumps({"round_id": round_id, "surface": "null"}))


def test_the_window_pools_the_last_w_rounds_and_archives_each_once(tmp_path):
    cfg = _cfg(tmp_path, window=2)
    for r in ("r0001", "r0002", "r0003"):
        _round_with_episode(cfg, r)
        pooled = window_archive(cfg, r)
    rounds = json.loads((pooled / "rounds.json").read_text())
    assert rounds == ["r0002", "r0003"]  # the oldest fell out of the window
    assert sorted(p.name for p in (cfg.state / "archive").iterdir()) == ["r0001", "r0002", "r0003"]
    # Re-archiving the same round is a no-op, so a re-run of the loop never double-counts.
    before = len(list((cfg.state / "archive" / "r0003").rglob("episode.json")))
    window_archive(cfg, "r0003")
    assert len(list((cfg.state / "archive" / "r0003").rglob("episode.json"))) == before


class _FakeApi:
    """Records what would be uploaded; serves back whatever index it was last given."""

    def __init__(self, token):
        self.uploads = []
        self.index = None

    def create_repo(self, *a, **k):
        pass

    def hf_hub_download(self, repo, name, **k):
        if self.index is None:
            raise FileNotFoundError(name)
        p = Path(k.get("_dir", "/tmp")) / "index.json"
        p.write_text(json.dumps(self.index))
        return str(p)

    def upload_file(self, *, path_or_fileobj, path_in_repo, **k):
        self.uploads.append(path_in_repo)
        if path_in_repo == "index.json":
            self.index = json.loads(path_or_fileobj.decode())


def _export(tmp_path: Path, digest="abc") -> Path:
    d = tmp_path / "export"
    d.mkdir(exist_ok=True)
    (d / "sft.jsonl").write_text("{}\n")
    (d / "dpo.jsonl").write_text("")
    (d / "manifest.json").write_text(
        json.dumps(
            {
                "round_id": "r1",
                "sft_rows": 1,
                "dpo_pairs": 0,
                "sft_sha256": digest,
                "dpo_sha256": "e3b0",
                "leak_scan": {"secrets_checked": 3, "rows_refused": 0},
            }
        )
    )
    return d


def test_upload_refuses_an_export_with_no_leak_scan(tmp_path, monkeypatch):
    d = _export(tmp_path)
    m = json.loads((d / "manifest.json").read_text())
    del m["leak_scan"]
    (d / "manifest.json").write_text(json.dumps(m))
    monkeypatch.setattr(up, "_api", lambda token: _FakeApi(token))
    try:
        up.upload(d, "org/repo", "tok")
    except SystemExit as e:
        assert "leak scan" in str(e)
    else:
        raise AssertionError("an export with no leak scan must not upload")


def test_upload_is_idempotent_per_round(tmp_path, monkeypatch):
    """The loop calls this every round; the same round twice must not duplicate anything."""
    api = _FakeApi("tok")
    monkeypatch.setattr(up, "_api", lambda token: api)
    d = _export(tmp_path)
    first = up.upload(d, "org/repo", "tok")
    assert first["uploaded"] and "rounds/r1/sft.jsonl" in api.uploads
    n = len(api.uploads)
    second = up.upload(d, "org/repo", "tok")
    assert not second["uploaded"] and "already present" in second["reason"]
    assert len(api.uploads) == n


def test_a_restart_resumes_the_unfinished_round_from_its_own_log(tmp_path):
    """Crash-safe resume (spec §5.7): the stages a round logged are skipped; the round it was in is picked up."""
    from sh.validator.orchestrate import done_stages, unfinished_round

    cfg = _cfg(tmp_path)
    assert unfinished_round(cfg) is None
    r1 = cfg.rounds / "r0001"
    r1.mkdir(parents=True)
    (r1 / "phases.jsonl").write_text(
        "\n".join(json.dumps({"t": 1, "stage": s}) for s in ("start", "mint", "seal", "publish_open")) + "\n"
    )
    assert unfinished_round(cfg) == r1
    assert done_stages(r1) == {"start", "mint", "seal", "publish_open"}
    (r1 / "DONE").write_text("{}")
    assert unfinished_round(cfg) is None  # a finished round is never resumed


def test_a_pull_request_changes_only_what_it_forked_with(tmp_path):
    """A crown merged into the base after a miner branched must not count as that miner's change — two-dot
    diffs said it did, and a well-formed PR would have been rejected as touching two directories."""
    import subprocess

    from sh.validator.orchestrate import _changed_submissions

    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    git("init", "-q", "-b", "main")
    (repo / "submissions").mkdir()
    (repo / "submissions" / "README.md").write_text("x")
    git("add", "."), git("commit", "-q", "-m", "base")
    git("checkout", "-q", "-b", "miner")
    (repo / "submissions" / "B").mkdir()
    (repo / "submissions" / "B" / "SOUL.md").write_text("Be careful.\n")
    git("add", "."), git("commit", "-q", "-m", "miner: B")
    git("checkout", "-q", "main")
    (repo / "submissions" / "A").mkdir()
    (repo / "submissions" / "A" / "SOUL.md").write_text("Be bold.\n")
    git("add", "."), git("commit", "-q", "-m", "crown: A")  # merged after the miner branched
    cfg = _cfg(tmp_path)
    cfg.repo = repo
    assert _changed_submissions(cfg, "main", git("rev-parse", "miner")) == ["B"]


def test_a_reopened_window_is_the_same_length_counts_itself_and_says_why():
    from sh.validator.orchestrate import reopened

    first = {"opens_at": 1000.0, "closes_at": 8200.0, "seconds": 7200}
    second = reopened(first, 7200, now=8300.0)
    assert second == {
        "opens_at": 8300.0,
        "closes_at": 15500.0,
        "seconds": 7200,
        "reopened": 1,
        "first_opened_at": 1000.0,
        "reason": "no submissions in window 1",
    }
    third = reopened(second, 7200, now=15600.0)
    assert (
        third["reopened"] == 2
        and third["first_opened_at"] == 1000.0
        and third["reason"] == "no submissions in window 2"
    )


def test_only_challengers_count_as_submissions():
    """An incumbent alone has nobody to defend against; evaluating it would spend the GPU on nothing."""
    from sh.validator.orchestrate import challenger_count

    assert challenger_count({}) == 0
    assert challenger_count({"KING": {"pr": None, "incumbent": True}}) == 0
    assert challenger_count({"KING": {"pr": None, "incumbent": True}, "A": {"pr": 7, "incumbent": False}}) == 1


def test_an_empty_window_reopens_the_round_instead_of_sealing_it(tmp_path, monkeypatch):
    """No seal, no evaluation, no new tasks: the same round waits again until someone submits."""
    import sh.validator.orchestrate as o

    cfg = _cfg(tmp_path)
    rd = cfg.rounds / "r0009"
    rd.mkdir(parents=True)
    for stage in ("start", "open"):
        o.log(rd, stage)
    calls: list[str] = []
    counts = iter([0, 0, 3])

    class Sealed(Exception):
        pass

    def fake_seal(*a, **k):
        raise Sealed

    monkeypatch.setattr(o, "wait_window", lambda cfg, rd, mock: calls.append("wait"))
    monkeypatch.setattr(o, "has_challengers", lambda cfg, round_id: next(counts))
    monkeypatch.setattr(o, "reopen_window", lambda cfg, rd: calls.append("reopen"))
    monkeypatch.setattr(o, "seal", fake_seal)
    try:
        o.run_round(cfg, resume=rd)
    except Sealed:
        pass
    assert calls == ["wait", "reopen", "wait", "reopen", "wait"]
    logged = [json.loads(line) for line in (rd / "phases.jsonl").read_text().splitlines()]
    assert logged[-1]["stage"] == "window" and logged[-1]["submissions"] == 3
