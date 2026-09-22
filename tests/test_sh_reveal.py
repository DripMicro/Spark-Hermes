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
    b = o._reveal_challenger(
        _cfg(tmp_path, repo), ref, hk, tmp_path / "staged", round_id="r0001", store=tmp_path / "empty"
    )
    assert b["problems"] and "no revealed bundle" in b["problems"][0]


def test_legacy_prose_pr_still_seals(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    ref = _commit_submission(
        repo, hk, {**PROSE, attest.FILE: (json.dumps(att) + "\n").encode()}
    )  # prose still in the PR
    b = o._reveal_challenger(
        _cfg(tmp_path, repo), ref, hk, tmp_path / "staged", round_id="r0001", store=tmp_path / "empty"
    )
    assert b and not b["problems"] and b["digest"] == digest


def test_seal_catches_a_tampered_stored_bundle(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk = kp.ss58_address
    att = attest.sign(kp, "r0001", bundle_digest(PROSE))  # commits to the real digest
    ref = _commit_submission(repo, hk, _attestation_only(att))
    store = _store(tmp_path, hk, att, {"SOUL.md": b"# Soul\n\nTampered prose that does not hash to the commitment.\n"})
    b = o._reveal_challenger(_cfg(tmp_path, repo), ref, hk, tmp_path / "staged", round_id="r0001", store=store)
    assert b["problems"] and any("bundle_sha256" in p for p in b["problems"])


def test_incumbent_resolves_from_the_private_store(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    kept = tmp_path / "state" / "incumbents" / hk  # the crowned bundle lives here, not in the public tree
    kept.mkdir(parents=True)
    (kept / "SOUL.md").write_bytes(PROSE["SOUL.md"])
    (kept / attest.FILE).write_text(json.dumps(att))
    b = o._incumbent_bundle(
        _cfg(tmp_path, repo), "HEAD", hk, tmp_path / "staged", incumbents=tmp_path / "state" / "incumbents"
    )
    assert b and not b["problems"] and b["digest"] == digest


def test_incumbent_falls_back_to_the_tree_when_not_in_the_store(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    ref = _commit_submission(
        repo, hk, {**PROSE, attest.FILE: (json.dumps(att) + "\n").encode()}
    )  # legacy: prose in tree
    b = o._incumbent_bundle(_cfg(tmp_path, repo), ref, hk, tmp_path / "staged", incumbents=tmp_path / "none")
    assert b and not b["problems"] and b["digest"] == digest


def test_retain_then_release_moves_the_bundle_through_the_store(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk, cfg = kp.ss58_address, _cfg(tmp_path, repo)
    rd = tmp_path / "rd"
    (rd / "bundles" / hk).mkdir(parents=True)
    (rd / "bundles" / hk / "SOUL.md").write_bytes(PROSE["SOUL.md"])
    (rd / "bundles" / hk / attest.FILE).write_text(json.dumps(attest.sign(kp, "r0001", bundle_digest(PROSE))))
    o._retain_incumbent(cfg, hk, rd)
    assert (cfg.state / "incumbents" / hk / "SOUL.md").exists()  # crowned bundle kept privately
    o._release_incumbent(cfg, hk, rd)
    assert (rd / "reveal" / hk / "SOUL.md").exists()  # dethroned: revealed for audit
    assert not (cfg.state / "incumbents" / hk).exists()  # and dropped from the store


def test_candidates_seals_a_private_incumbent_from_the_store(tmp_path, monkeypatch):
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    _commit_submission(repo, hk, _attestation_only(att))  # public marker: the commitment only, no prose
    kept = tmp_path / "state" / "incumbents" / hk
    kept.mkdir(parents=True)
    (kept / "SOUL.md").write_bytes(PROSE["SOUL.md"])
    (kept / attest.FILE).write_text(json.dumps(att))
    cfg = _cfg(tmp_path, repo)
    (cfg.rounds / "r0002").mkdir(parents=True)  # similarity.load reads the round dir (no answers)

    def fake_sh(cmd, **k):
        if cmd[:2] == ["git", "ls-tree"] and cmd[-1] == "submissions/":
            return f"submissions/{hk}\nsubmissions/README.md\n"
        return ""

    monkeypatch.setattr(o, "sh", fake_sh)
    monkeypatch.setattr(o, "_strategy_prs", lambda cfg, tip: [])
    active, rejected = o.candidates(cfg, "r0002", tmp_path / "bundles")
    assert list(active) == [hk] and active[hk]["incumbent"] and active[hk]["bundle_sha256"] == digest
    assert rejected == {}


def test_reveal_publishes_out_of_competition_bundles_but_not_the_king(tmp_path):
    rd, dest = tmp_path / "rd", tmp_path / "dest"
    rd.mkdir()
    dest.mkdir()
    king = "5" + "A" * 47
    loser = "5" + "B" * 47
    incumbent = "5" + "C" * 47
    dethroned = "5" + "D" * 47
    (rd / "seal.json").write_text(
        json.dumps(
            {
                "active": {
                    king: {"pr": 1, "incumbent": False},
                    loser: {"pr": 2, "incumbent": False},
                    incumbent: {"pr": None, "incumbent": True},
                }
            }
        )
    )
    for hk in (king, loser, incumbent):
        d = rd / "bundles" / hk
        d.mkdir(parents=True)
        (d / "SOUL.md").write_text(f"soul {hk[:6]}\n")
    d = rd / "reveal" / dethroned  # staged by _release_incumbent when it was dethroned this round
    d.mkdir(parents=True)
    (d / "SOUL.md").write_text("old king\n")
    cfg = _cfg(tmp_path, tmp_path / "repo-unused")
    (cfg.state / "incumbents" / incumbent).mkdir(parents=True)  # still defending: its prose stays private
    o._reveal_bundles(cfg, rd, dest, king)
    published = sorted(p.name for p in (dest / "revealed").iterdir())
    assert published == sorted([loser, dethroned])  # king + staying incumbent withheld; loser + dethroned revealed


def test_a_forged_digest_cannot_escape_the_store(tmp_path):
    """bundle_sha256 comes out of the miner's own attestation, so it is attacker-controlled: it names a directory
    in the private store and must never be able to climb out of it."""
    repo, kp = _repo(tmp_path), _kp()
    hk = kp.ss58_address
    att = attest.sign(kp, "r0001", bundle_digest(PROSE))
    att["bundle_sha256"] = "../../../../../../tmp"  # not a digest: a path
    ref = _commit_submission(repo, hk, _attestation_only(att))
    store = tmp_path / "store"
    store.mkdir()
    staged = tmp_path / "staged"
    b = o._reveal_challenger(_cfg(tmp_path, repo), ref, hk, staged, round_id="r0001", store=store)
    assert b is not None and b["problems"]  # refused
    assert not staged.exists()  # refused before anything at all was materialised


def test_a_pr_that_did_not_sign_cannot_claim_another_hotkeys_submission(tmp_path):
    """The PR's own attestation must carry the hotkey's signature. Without that check a one-file PR copying a
    victim's public digest pointed the seal at the victim's revealed bundle and took the slot: the victim's real
    PR was closed as superseded and the attacker's login was published as that hotkey's identity."""
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    store = _store(tmp_path, hk, att, PROSE)  # the victim's bundle really is in the store
    forged = {**att, "signature": "0x" + "00" * 64}  # ...but the attacker signed nothing
    ref = _commit_submission(repo, hk, _attestation_only(forged))
    staged = tmp_path / "staged"
    b = o._reveal_challenger(_cfg(tmp_path, repo), ref, hk, staged, round_id="r0001", store=store)
    assert b["problems"] and any("signature" in p for p in b["problems"])
    assert not staged.exists()  # the victim's prose was never materialised under the attacker's PR


def test_a_hotkey_still_defending_is_not_revealed(tmp_path):
    """A reigning king that resubmits and is not dethroned keeps defending, so its new prose must stay private —
    'not crowned this round' is not the same as 'out of the competition'."""
    rd, dest = tmp_path / "rd", tmp_path / "dest"
    rd.mkdir()
    dest.mkdir()
    king, loser, defender = "5" + "A" * 47, "5" + "B" * 47, "5" + "C" * 47
    (rd / "seal.json").write_text(
        json.dumps(
            {
                "active": {
                    king: {"pr": 1, "incumbent": False},
                    loser: {"pr": 2, "incumbent": False},
                    # the reigning king, resubmitted this round as a challenger and NOT dethroned
                    defender: {"pr": 3, "incumbent": False, "was_incumbent": True},
                }
            }
        )
    )
    for hk in (king, loser, defender):
        d = rd / "bundles" / hk
        d.mkdir(parents=True)
        (d / "SOUL.md").write_text(f"soul {hk[:6]}\n")
    cfg = _cfg(tmp_path, tmp_path / "repo-unused")
    (cfg.state / "incumbents" / defender).mkdir(parents=True)  # still held: still defending
    o._reveal_bundles(cfg, rd, dest, king)
    assert sorted(p.name for p in (dest / "revealed").iterdir()) == [loser]
