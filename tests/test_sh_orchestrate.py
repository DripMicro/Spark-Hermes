"""The loop's pure parts: round numbering, window pooling, the one-crown rule, and the upload's idempotence.
The stages that touch GitHub and the GPU are exercised by the real loop, not here."""

from __future__ import annotations

import json
from pathlib import Path

import sh.exports.upload as up
from sh.validator.orchestrate import Config, window_archive


def _cfg(tmp_path: Path, window: int = 8) -> Config:
    return Config(
        state=tmp_path / "state",
        repo=tmp_path / "repo",
        queue=tmp_path / "queue",
        pkg=tmp_path,
        window=window,
        window_from="r0000",
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


def test_a_forged_later_resubmission_cannot_take_a_miners_real_submission_out_of_the_round(tmp_path, monkeypatch):
    """#12 reopens A's bundle with signed_at moved later: the signature breaks. Choosing before verifying would have
    picked #12, rejected it, and dropped #7 — A's real submission — with it."""
    import sh.validator.orchestrate as o

    cfg = _cfg(tmp_path)
    (cfg.rounds / "r0009" / "tasks").mkdir(parents=True)
    HKA, HKB = "5" + "A" * 47, "5" + "B" * 47  # ss58-shaped
    prs = [
        {"number": 7, "headRefOid": "h7", "changed": [HKA]},
        {"number": 12, "headRefOid": "h12", "changed": [HKA]},
        {"number": 9, "headRefOid": "h9", "changed": [HKB]},
    ]
    signed = {
        "h7": (2000, []),
        "h12": (9000, ["L10 attestation.json: signature is not the hotkey's over this round and digest"]),
        "h9": (1500, []),
    }

    def fake_bundle(cfg, ref, hotkey, dest, *, round_id):
        at, problems = signed[ref]
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "SOUL.md").write_text("Be careful.\n")
        (dest / "attestation.json").write_text(json.dumps({"signed_at": at}))
        return {"problems": problems, "digest": "d-" + ref, "attestation": None}

    monkeypatch.setattr(o, "sh", lambda *a, **k: "")
    monkeypatch.setattr(o, "_strategy_prs", lambda cfg, tip: prs)
    monkeypatch.setattr(o, "_bundle_from_tree", fake_bundle)
    head_hk = {"h7": HKA, "h12": HKA, "h9": HKB}
    monkeypatch.setattr(o, "_changed_paths", lambda cfg, base, head: [f"submissions/{head_hk[head]}/SOUL.md"])
    active, rejected = o.candidates(cfg, "r0009", tmp_path / "bundles")
    assert active[HKA]["pr"] == 7 and active[HKB]["pr"] == 9
    assert rejected == {"12": "L10 attestation.json: signature is not the hotkey's over this round and digest"}
    assert sorted(p.name for p in (tmp_path / "bundles").iterdir()) == sorted([HKA, HKB])  # staging cleaned up


def test_the_credit_window_does_not_pool_rounds_scored_all_or_nothing(tmp_path):
    """Rounds before sh-scoring-v3 carry no credit: pooling them would drag every reference toward zero."""
    cfg = _cfg(tmp_path)
    cfg.window_from = "r0004"
    for rid in ("r0002", "r0003", "r0004", "r0005"):
        (cfg.state / "archive" / rid).mkdir(parents=True)
    (cfg.rounds / "r0005").mkdir(parents=True)
    pooled = window_archive(cfg, "r0005")
    assert json.loads((pooled / "rounds.json").read_text()) == ["r0004", "r0005"]


def test_a_round_closed_before_the_credit_window_still_scores_itself(tmp_path):
    cfg = _cfg(tmp_path)
    cfg.window_from = "r0004"
    for rid in ("r0002", "r0003"):
        (cfg.state / "archive" / rid).mkdir(parents=True)
    pooled = window_archive(cfg, "r0003")
    assert json.loads((pooled / "rounds.json").read_text()) == ["r0003"]


def test_a_previewing_family_shows_miners_its_previews_and_publishes_the_evaluated_tasks_only_at_close(tmp_path):
    import sh.validator.orchestrate as o

    rd = tmp_path / "r0005"
    (rd / "tasks").mkdir(parents=True)
    (rd / "tasks" / "swe-fix-r0005-00.json").write_text("{}")
    assert o.shown(rd) == rd / "tasks"  # a family without previews: the tasks themselves
    (rd / "preview").mkdir()
    (rd / "preview" / "swe-fix-r0005-p00.json").write_text("{}")
    assert o.shown(rd) == rd / "preview"


def test_evaluation_claims_the_engine_before_it_waits_and_releases_the_claim_once_its_batch_runs(tmp_path, monkeypatch):
    """The daemon screens buffered candidates seconds apart; the claim stops it starting another while this side
    waits for the running one to end, and is held until the batch is visible."""
    import sh.validator.orchestrate as o

    cfg = _cfg(tmp_path)
    rd = cfg.rounds / "r0005"
    (rd / "tasks").mkdir(parents=True)
    (rd / "tasks" / "swe-fix-r0005-00.json").write_text("{}")
    calls, state = [], {"screen": 2, "batch": False}

    def worker(cfg, cmd):
        if "pgrep -f '[b]atch --round /root/sh/screen/'" in cmd:
            calls.append("screen?")
            state["screen"] -= 1
            return "1" if state["screen"] > 0 else "0"
        if "pgrep -f '[b]atch --round /root/sh/rounds/r0005'" in cmd:
            calls.append("batch?")
            return "1" if state["batch"] else "0"
        if "engine-claim" in cmd:
            calls.append("claim" if "touch" in cmd else "release")
        return ""

    def launch(cfg, cmd):
        calls.append("launch")
        state["batch"] = True

    def rsync_back(src, dst, cfg):
        if "episodes" in src:  # the batch finished: one episode came back
            ep = rd / "episodes" / "null" / "swe-fix-r0005-00"
            ep.mkdir(parents=True, exist_ok=True)
            (ep / "episode.json").write_text("{}")
            state["batch"] = False

    ticks = iter([True, False])  # the batch runs for one poll, then ends with everything done
    monkeypatch.setattr(o, "_worker", worker)
    monkeypatch.setattr(o, "_worker_launch", launch)
    monkeypatch.setattr(o, "_rsync", rsync_back)
    monkeypatch.setattr(o, "_progress", lambda cfg, remote, total: {"done": total, "total": total, "by_surface": {}})
    monkeypatch.setattr(o, "live", lambda *a, **k: None)
    monkeypatch.setattr(o.time, "sleep", lambda s: state.__setitem__("batch", next(ticks, False)) if s == 45 else None)
    o.evaluate(cfg, rd, {"active": []})
    first = calls.index("claim")
    assert calls[first + 1] == "screen?" and calls.index("launch") > calls.index("screen?")
    assert (
        calls.index("release") > calls.index("launch")
        and "batch?" in calls[calls.index("launch") : calls.index("release")]
    )
    assert calls.count("claim") == calls.count("release") == 1


def test_a_strategy_pr_that_touches_anything_but_its_own_submission_directory_is_rejected(tmp_path, monkeypatch):
    """A crowned PR is merged; a PR that also edits sh/ or another hotkey's directory would merge arbitrary code."""
    import sh.validator.orchestrate as o

    cfg = _cfg(tmp_path)
    (cfg.rounds / "r0009" / "tasks").mkdir(parents=True)
    HK = "5" + "C" * 47
    prs = [
        {"number": 3, "headRefOid": "h3", "changed": [HK]},  # touches sh/ too
        {"number": 4, "headRefOid": "h4", "changed": ["not-an-ss58"]},
        {"number": 5, "headRefOid": "h5", "changed": [HK]},  # clean
    ]
    diffs = {
        "h3": [f"submissions/{HK}/SOUL.md", "sh/validator/grade.py"],
        "h4": ["submissions/not-an-ss58/SOUL.md"],
        "h5": [f"submissions/{HK}/SOUL.md"],
    }

    def fake_bundle(cfg, ref, hotkey, dest, *, round_id):
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "SOUL.md").write_text("Be careful.\n")
        (dest / "attestation.json").write_text(json.dumps({"signed_at": 100}))
        return {"problems": [], "digest": "d-" + ref, "attestation": None}

    monkeypatch.setattr(o, "sh", lambda *a, **k: "")
    monkeypatch.setattr(o, "_strategy_prs", lambda cfg, tip: prs)
    monkeypatch.setattr(o, "_bundle_from_tree", fake_bundle)
    monkeypatch.setattr(o, "_changed_paths", lambda cfg, base, head: diffs[head])
    active, rejected = o.candidates(cfg, "r0009", tmp_path / "bundles")
    assert set(active) == {HK} and active[HK]["pr"] == 5
    assert "outside" in rejected["3"] and "ss58" in rejected["4"]


def test_a_resubmitting_incumbent_that_loses_is_still_dethroned():
    from sh.validator.orchestrate import dethroned

    sealed = {
        "active": {
            "5A": {"incumbent": True},  # a plain incumbent
            "5B": {"incumbent": False, "was_incumbent": True, "pr": 9},  # incumbent that resubmitted and lost
            "5C": {"incumbent": False, "pr": 10},  # a fresh challenger, never an incumbent
        }
    }
    assert dethroned(sealed, king="5C") == ["5A", "5B"]  # both old bundles leave submissions/; the fresh king stays
    assert dethroned(sealed, king="5A") == ["5B"]


def test_a_hugging_face_failure_does_not_block_the_round(tmp_path, monkeypatch):
    import sh.validator.orchestrate as o

    cfg = _cfg(tmp_path)
    rd = cfg.rounds / "r0009"
    (rd / "export").mkdir(parents=True)
    monkeypatch.setattr(o, "build_exports", lambda *a, **k: {"sft_rows": 1, "dpo_pairs": 0})
    monkeypatch.setattr(o, "upload_exports", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("HF 401")))
    monkeypatch.setenv("HF_TOKEN", "tok")
    result = o.export_and_upload(cfg, "r0009", rd, king="5A")  # must return, not raise
    assert result["upload"]["uploaded"] is False and "HF 401" in result["upload"]["reason"]


def test_the_archive_holds_only_episode_records_not_snapshots(tmp_path):
    from sh.validator.orchestrate import window_archive

    cfg = _cfg(tmp_path, window=2)
    d = cfg.rounds / "r0005" / "episodes" / "null" / "t0"
    d.mkdir(parents=True)
    (d / "episode.json").write_text(json.dumps({"round_id": "r0005", "surface": "null"}))
    (d / "snapshot.tar").write_bytes(b"\x00" * 5000)  # the heavy part
    (d / "trajectory.json").write_text("[]")
    pooled = window_archive(cfg, "r0005")
    archived = [p.name for p in (cfg.state / "archive" / "r0005").rglob("*") if p.is_file()]
    assert archived == ["episode.json"] and not list((cfg.state / "archive" / "r0005").rglob("snapshot.tar"))
    assert (pooled / "r0005" / "null" / "t0" / "episode.json").exists()


def test_reclaim_strips_heavy_files_from_old_done_rounds_but_keeps_recent_and_records(tmp_path):
    from sh.validator.orchestrate import _reclaim_disk

    cfg = _cfg(tmp_path)
    for rid in ("r0003", "r0004", "r0005"):
        d = cfg.rounds / rid / "episodes" / "null" / "t0"
        d.mkdir(parents=True)
        (d / "episode.json").write_text("{}")
        (d / "snapshot.tar").write_bytes(b"x" * 100)
        (d / "trajectory.json").write_text("[]")
        (cfg.rounds / rid / "DONE").write_text("{}")
    _reclaim_disk(cfg, keep_recent=2)
    # r0003 is old: stripped; r0004/r0005 are the two most recent: kept; episode.json survives everywhere
    assert not (cfg.rounds / "r0003" / "episodes" / "null" / "t0" / "snapshot.tar").exists()
    assert (cfg.rounds / "r0003" / "episodes" / "null" / "t0" / "episode.json").exists()
    assert (cfg.rounds / "r0004" / "episodes" / "null" / "t0" / "snapshot.tar").exists()
    assert (cfg.rounds / "r0005" / "episodes" / "null" / "t0" / "trajectory.json").exists()


def test_live_json_carries_a_hotkey_to_github_map_accumulated_across_rounds(tmp_path, monkeypatch):
    import sh.validator.orchestrate as o

    cfg = _cfg(tmp_path)
    rd = cfg.rounds / "r0006"
    rd.mkdir(parents=True)
    (rd / "window.json").write_text(json.dumps({"opens_at": 1.0, "closes_at": 2.0, "seconds": 1}))
    (rd / "seal.json").write_text(json.dumps({"active": {"5B": {"pr": 8, "github": "octocat"}}}))
    (cfg.repo).mkdir(parents=True, exist_ok=True)
    (cfg.repo / "docs" / "live").mkdir(parents=True)
    (cfg.repo / "docs" / "live" / "live.json").write_text(
        json.dumps({"round_id": "r0006", "github": {"5A": "torvalds"}})
    )
    monkeypatch.setattr(o, "_commit", lambda *a, **k: None)
    o.live(cfg, rd, "window", submissions=[{"hotkey": "5C", "pr": 9, "github": "gvanrossum"}], push=False)
    live = json.loads((cfg.repo / "docs" / "live" / "live.json").read_text())
    assert live["github"] == {"5A": "torvalds", "5B": "octocat", "5C": "gvanrossum"}  # prev + seal + submissions
