"""The seal's reveal step: a challenger's prose comes from the private store by the digest its public
attestation committed to — with a fallback to the PR tree while miners are still migrating — and the seal
re-checks it, so a commitment with no reveal, or a store bundle that does not hash to the commitment, is
refused."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

import sh.validator.orchestrate as o
from sh.cli import attest
from sh.cli.lint import bundle_digest
from sh.validator.orchestrate import Config

substrate = pytest.importorskip("substrateinterface")

PROSE = {"SOUL.md": b"# Soul\n\nReproduce the failing test, then fix the source.\n"}


def _kp(uri: str = "//Alice"):
    return substrate.Keypair.create_from_uri(uri, crypto_type=substrate.KeypairType.SR25519)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "README.md").write_text("x\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    return repo


def _cfg(tmp_path: Path, repo: Path) -> Config:
    return Config(state=tmp_path / "state", repo=repo, queue=tmp_path / "q", pkg=tmp_path)


def _commit_submission(repo: Path, hotkey: str, files: dict[str, bytes]) -> str:
    d = repo / "submissions" / hotkey
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    for rel, data in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "submission")
    return _git(repo, "rev-parse", "HEAD").strip()


def _store(tmp_path: Path, hotkey: str, att: dict, files: dict[str, bytes]) -> Path:
    store = tmp_path / "store"
    dest = store / att["round_id"] / hotkey / "uploads" / f"{att['signed_at']}-{att['bundle_sha256']}"
    dest.mkdir(parents=True)
    for rel, data in files.items():
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    (dest / attest.FILE).write_text(json.dumps(att))
    (dest / "receipt.json").write_text(json.dumps({"schema": "sh-receipt-v1"}))
    return store


def _attestation_only(att: dict) -> dict[str, bytes]:
    return {attest.FILE: (json.dumps(att) + "\n").encode()}


def test_store_first_reveals_the_committed_bundle(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    ref = _commit_submission(repo, hk, _attestation_only(att))  # the PR carries only the commitment
    store = _store(tmp_path, hk, att, PROSE)
    dest = tmp_path / "staged"
    b = o._reveal_challenger(_cfg(tmp_path, repo), ref, hk, dest, round_id="r0001", store=store)
    assert b and not b["problems"] and b["digest"] == digest
    assert (dest / "SOUL.md").exists() and not (dest / "receipt.json").exists()  # prose in, receipt not


def test_commit_without_reveal_is_rejected(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk = kp.ss58_address
    att = attest.sign(kp, "r0001", bundle_digest(PROSE))
    ref = _commit_submission(repo, hk, _attestation_only(att))  # committed, but nothing in the store
    b = o._reveal_challenger(_cfg(tmp_path, repo), ref, hk, tmp_path / "staged", round_id="r0001", store=tmp_path / "empty")
    assert b["problems"] and "no revealed bundle" in b["problems"][0]


def test_legacy_prose_pr_still_seals(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    ref = _commit_submission(repo, hk, {**PROSE, attest.FILE: (json.dumps(att) + "\n").encode()})  # prose still in the PR
    b = o._reveal_challenger(_cfg(tmp_path, repo), ref, hk, tmp_path / "staged", round_id="r0001", store=tmp_path / "empty")
    assert b and not b["problems"] and b["digest"] == digest


def test_seal_catches_a_tampered_stored_bundle(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk = kp.ss58_address
    att = attest.sign(kp, "r0001", bundle_digest(PROSE))  # commits to the real digest
    ref = _commit_submission(repo, hk, _attestation_only(att))
    store = _store(tmp_path, hk, att, {"SOUL.md": b"# Soul\n\nTampered prose that does not hash to the commitment.\n"})
    b = o._reveal_challenger(_cfg(tmp_path, repo), ref, hk, tmp_path / "staged", round_id="r0001", store=store)
    assert b["problems"] and any("bundle_sha256" in p for p in b["problems"])
