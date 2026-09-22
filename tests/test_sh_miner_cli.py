"""The miner CLI's fork-resubmit path: a fork's open PR is found by branch and owner, not by `owner:branch`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import sh.cli.miner as miner
from sh.cli import attest
from sh.cli.lint import bundle_digest

substrate = pytest.importorskip("substrateinterface")


def _kp(uri: str = "//Alice"):
    return substrate.Keypair.create_from_uri(uri, crypto_type=substrate.KeypairType.SR25519)


def _bundle(tmp_path: Path, text: str = "# Soul\n\nReproduce the failing test, then fix the source.\n") -> Path:
    b = tmp_path / "bundle"
    b.mkdir()
    (b / "SOUL.md").write_text(text)
    return b


def _fake_git_gh(recorder: dict):
    """Stand in for git+gh: record what `git add` staged under submissions/<hotkey>/, and open PR #7."""
    def fake_run(cmd, cwd=None, check_rc=True):
        if cmd[:2] == ["git", "add"] and cwd is not None:
            hotkey_dir = next((Path(cwd) / "submissions").iterdir())
            recorder["written"] = sorted(p.name for p in hotkey_dir.iterdir())
        if cmd[:3] == ["gh", "pr", "list"]:
            return "[]"
        if cmd[:3] == ["gh", "pr", "create"]:
            return "https://github.com/org/repo/pull/7"
        return ""

    return fake_run


def test_an_open_fork_pr_is_found_by_branch_and_owner(monkeypatch):
    calls = []

    def fake_run(cmd, cwd=None, check_rc=True):
        calls.append(cmd)
        if cmd[:3] == ["gh", "pr", "list"]:
            return json.dumps(
                [
                    {"number": 41, "headRepositoryOwner": {"login": "someone-else"}},
                    {"number": 42, "headRepositoryOwner": {"login": "alice"}},
                ]
            )
        return ""

    monkeypatch.setattr(miner, "_run", fake_run)
    assert miner._open_pr_for("org/repo", "main", "miner/5HK", "alice") == 42
    assert miner._open_pr_for("org/repo", "main", "miner/5HK", "nobody") is None
    assert miner._open_pr_for("org/repo", "main", "miner/5HK") == 41  # no owner filter: the first open PR
    assert all("alice:miner/5HK" not in " ".join(c) for c in calls)  # never the owner:branch form gh returns empty for


def test_private_mode_uploads_prose_and_commits_only_the_commitment(monkeypatch, tmp_path):
    kp = _kp()
    captured = {}

    def fake_upload(server, att, files):
        captured["server"], captured["uploaded"] = server, sorted(files)
        return {"ok": True, "receipt": {"schema": "sh-receipt-v1", "digest": att["bundle_sha256"]}}

    rec = {}
    monkeypatch.setattr(miner, "_upload", fake_upload)
    monkeypatch.setattr(miner, "_run", _fake_git_gh(rec))
    r = miner.submit_bundle(_bundle(tmp_path), kp, round_id="r0001", checkout=tmp_path, server="http://ingest")
    assert r["ok"] and r["private"] and r["pr"] == 7
    assert captured["uploaded"] == ["SOUL.md"]  # the prose went to the private server
    assert rec["written"] == ["attestation.json", "receipt.json"]  # the PR carries only the commitment


def test_legacy_mode_commits_the_prose(monkeypatch, tmp_path):
    rec = {}
    monkeypatch.setattr(miner, "_run", _fake_git_gh(rec))
    r = miner.submit_bundle(_bundle(tmp_path), _kp(), round_id="r0001", checkout=tmp_path)  # no server
    assert r["ok"] and not r.get("private")
    assert rec["written"] == ["SOUL.md", "attestation.json"]


def test_server_rejection_is_surfaced_without_touching_git(monkeypatch, tmp_path):
    monkeypatch.setattr(miner, "_upload", lambda *a, **k: {"ok": False, "problems": ["S1 reproduces answers"]})
    ran = []
    monkeypatch.setattr(miner, "_run", lambda *a, **k: ran.append(a) or "")
    r = miner.submit_bundle(_bundle(tmp_path), _kp(), round_id="r0001", checkout=tmp_path, server="http://x")
    assert not r["ok"] and r["problems"] == ["S1 reproduces answers"]
    assert not ran  # a rejected upload never runs git or gh


def test_committed_digest_reads_the_attestation_in_private_mode(tmp_path):
    kp, files = _kp(), {"SOUL.md": b"# Soul\n\nDebug carefully.\n"}
    digest = bundle_digest(files)
    dest = tmp_path / "submissions" / kp.ss58_address
    dest.mkdir(parents=True)
    (dest / attest.FILE).write_text(json.dumps(attest.sign(kp, "r0001", digest)))
    assert miner._committed_digest(dest, private=True) == digest
    (dest / "SOUL.md").write_bytes(files["SOUL.md"])
    assert miner._committed_digest(dest, private=False) == digest  # legacy: over the committed prose


def test_upload_reaches_a_real_ingest_server(tmp_path):
    import threading
    import time
    from http.server import ThreadingHTTPServer

    from sh.server import ingest

    rd = tmp_path / "state" / "rounds" / "r0001"
    for s in ("private", "withheld", "tasks", "preview"):
        (rd / s).mkdir(parents=True)
    (rd / "window.json").write_text(json.dumps({"opens_at": 0, "closes_at": time.time() + 3600, "seconds": 7200}))
    store = tmp_path / "store"
    store.mkdir()
    handler = ingest.make_handler(
        state=tmp_path / "state", store=store, gate=ingest.allow_all, secret=None, limiter=ingest._RateLimiter(200, 5000)
    )
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        kp, files = _kp(), {"SOUL.md": b"# Soul\n\nReproduce, then fix.\n"}
        att = attest.sign(kp, "r0001", bundle_digest(files))
        out = miner._upload(f"http://127.0.0.1:{httpd.server_address[1]}", att, files)
    finally:
        httpd.shutdown()
    assert out["ok"] and out["receipt"]["digest"] == att["bundle_sha256"]
