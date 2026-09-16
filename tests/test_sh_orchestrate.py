"""The loop's pure parts: round numbering, window pooling, the one-crown rule, and the upload's idempotence.
The stages that touch GitHub and the GPU are exercised by the real loop, not here."""

from __future__ import annotations

import json
from pathlib import Path

import sh.exports.upload as up
from sh.validator.orchestrate import Config, next_round_id, window_archive


def _cfg(tmp_path: Path, window: int = 8) -> Config:
    return Config(state=tmp_path / "state", repo=tmp_path / "repo", supply=tmp_path, pkg=tmp_path, window=window)


def test_rounds_are_numbered_from_what_is_on_disk(tmp_path):
    cfg = _cfg(tmp_path)
    assert next_round_id(cfg) == "r0001"
    (cfg.rounds / "r0001").mkdir(parents=True)
    (cfg.rounds / "r0007").mkdir()
    assert next_round_id(cfg) == "r0008"  # gaps do not matter; the latest does


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
