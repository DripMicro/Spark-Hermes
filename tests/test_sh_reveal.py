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
    assert not (cfg.state / "incumbents" / f".{hk}.new").exists()  # the swap's scratch dirs do not outlive it
    assert not (cfg.state / "incumbents" / f".{hk}.old").exists()
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


def _sealed(rd, entries):
    (rd / "seal.json").write_text(json.dumps({"active": entries}))
    for hk in entries:
        d = rd / "bundles" / hk
        d.mkdir(parents=True, exist_ok=True)
        (d / "SOUL.md").write_text(f"soul {hk[:6]}\n")


def _defends(cfg, hotkey, digest):
    """Put a hotkey in the private incumbents store, defending the bundle named by `digest`."""
    d = cfg.state / "incumbents" / hotkey
    d.mkdir(parents=True, exist_ok=True)
    (d / attest.FILE).write_text(json.dumps({"bundle_sha256": digest}))
    (d / "SOUL.md").write_text("the bundle it was crowned on\n")


def test_reveal_publishes_what_is_out_and_withholds_what_defends(tmp_path):
    rd, dest = tmp_path / "rd", tmp_path / "dest"
    rd.mkdir()
    dest.mkdir()
    king, loser, holder, dethroned = ("5" + c * 47 for c in "ABCD")
    _sealed(
        rd,
        {
            king: {"pr": 1, "incumbent": False, "bundle_sha256": "k" * 64},
            loser: {"pr": 2, "incumbent": False, "bundle_sha256": "l" * 64},
            holder: {"pr": None, "incumbent": True, "bundle_sha256": "h" * 64},
        },
    )
    cfg = _cfg(tmp_path, tmp_path / "repo-unused")
    _defends(cfg, holder, "h" * 64)  # defending with this exact bundle
    d = rd / "reveal" / dethroned  # released this round by _release_incumbent
    d.mkdir(parents=True)
    (d / "SOUL.md").write_text("old king\n")
    (d / attest.FILE).write_text(json.dumps({"bundle_sha256": "d" * 64}))

    o._reveal_bundles(cfg, rd, dest, king)
    assert sorted(p.name for p in (dest / "revealed").iterdir()) == sorted([loser, dethroned])


def test_a_bundle_its_owner_no_longer_defends_is_revealed(tmp_path):
    """A reigning king that resubmits and is not dethroned keeps defending on its OLD bundle. The new one it just
    lost with is out of the competition, and its commitment is public, so it has to be revealed."""
    rd, dest = tmp_path / "rd", tmp_path / "dest"
    rd.mkdir()
    dest.mkdir()
    defender = "5" + "D" * 47
    _sealed(rd, {defender: {"pr": 3, "incumbent": False, "was_incumbent": True, "bundle_sha256": "new" + "0" * 61}})
    cfg = _cfg(tmp_path, tmp_path / "repo-unused")
    _defends(cfg, defender, "old" + "0" * 61)  # still defending, but on a DIFFERENT bundle

    o._reveal_bundles(cfg, rd, dest, king=None)
    assert [p.name for p in (dest / "revealed").iterdir()] == [defender]
    assert (dest / "revealed" / defender / "SOUL.md").read_text().startswith("soul")  # this round's, not the crown's


def test_an_ordinary_dethronement_publishes_one_copy(tmp_path):
    """The sealed bundle and the staged one are the same bundle; publishing both left a phantom duplicate."""
    rd, dest = tmp_path / "rd", tmp_path / "dest"
    rd.mkdir()
    dest.mkdir()
    king, gone = "5" + "K" * 47, "5" + "G" * 47
    _sealed(
        rd,
        {
            king: {"pr": 1, "incumbent": False, "bundle_sha256": "k" * 64},
            gone: {"pr": None, "incumbent": True, "bundle_sha256": "g" * 64},
        },
    )
    cfg = _cfg(tmp_path, tmp_path / "repo-unused")
    d = rd / "reveal" / gone  # _release_incumbent staged it and removed the store entry
    d.mkdir(parents=True)
    (d / "SOUL.md").write_text("soul 5GGGGG\n")
    (d / attest.FILE).write_text(json.dumps({"bundle_sha256": "g" * 64}))

    o._reveal_bundles(cfg, rd, dest, king)
    assert [p.name for p in (dest / "revealed").iterdir()] == [gone]  # exactly one, no ".dethroned" phantom


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


def test_an_incumbent_no_marker_claims_is_released_not_left_to_rot(tmp_path, monkeypatch):
    """A crown that never landed, or a marker removed outside the dethrone path, left a store entry defending
    nothing — and the reveal skips a hotkey still in the store, so it was never published either."""
    repo = _repo(tmp_path)
    cfg = _cfg(tmp_path, repo)
    rd = tmp_path / "rd"
    rd.mkdir()
    claimed, orphan = "5" + "C" * 47, "5" + "O" * 47
    for hk in (claimed, orphan):
        d = cfg.state / "incumbents" / hk
        d.mkdir(parents=True)
        (d / "SOUL.md").write_text(f"soul {hk[:6]}\n")
        (d / attest.FILE).write_text(json.dumps({"bundle_sha256": "a" * 64}))

    monkeypatch.setattr(o, "sh", lambda *a, **k: f"submissions/{claimed}\nsubmissions/README.md\n")
    assert o._prune_orphan_incumbents(cfg, rd) == [orphan]
    assert (cfg.state / "incumbents" / claimed).is_dir()  # the one a marker claims still defends
    assert not (cfg.state / "incumbents" / orphan).exists()  # the orphan is gone
    assert (rd / "reveal" / orphan / "SOUL.md").exists()  # ...and revealed rather than lost


def test_a_failed_marker_listing_does_not_release_every_crown(tmp_path, monkeypatch):
    """`git ls-tree` prints nothing when it fails. The prune used to read that as an empty tree and release
    every crown — and publish every bundle — because a hotkey still in the store is skipped by the reveal."""
    repo = _repo(tmp_path)
    cfg = _cfg(tmp_path, repo)
    rd = tmp_path / "rd"
    rd.mkdir()
    claimed, orphan = "5" + "C" * 47, "5" + "B" * 47
    for hk in (claimed, orphan):
        d = cfg.state / "incumbents" / hk
        d.mkdir(parents=True)
        (d / "SOUL.md").write_text(f"soul {hk[:6]}\n")

    def fail(*_a, **_k):
        raise RuntimeError("git ls-tree… exited 128: fatal: not a git repository")

    monkeypatch.setattr(o, "sh", fail)
    assert o._prune_orphan_incumbents(cfg, rd) == []
    assert (cfg.state / "incumbents" / claimed).is_dir()
    assert (cfg.state / "incumbents" / orphan).is_dir()
    assert not (rd / "reveal").exists()


def test_a_real_empty_listing_still_releases_what_nobody_claims(tmp_path, monkeypatch):
    """Failure is not emptiness. A listing that succeeded and named nobody still means nothing defends."""
    repo = _repo(tmp_path)
    cfg = _cfg(tmp_path, repo)
    rd = tmp_path / "rd"
    rd.mkdir()
    orphan = "5" + "B" * 47
    d = cfg.state / "incumbents" / orphan
    d.mkdir(parents=True)
    (d / "SOUL.md").write_text("soul\n")
    monkeypatch.setattr(o, "sh", lambda *_a, **_k: "")
    assert o._prune_orphan_incumbents(cfg, rd) == [orphan]
    assert (rd / "reveal" / orphan / "SOUL.md").exists()


def test_a_retain_interrupted_before_the_swap_still_defends(tmp_path):
    """The new bundle was written and the previous crown moved aside, then the process died before the rename.
    The next seal has to defend with that bundle, not report the king unresolved and not publish the scratch dir."""
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    store = tmp_path / "state" / "incumbents"
    staging = store / f".{hk}.new"
    staging.mkdir(parents=True)
    (staging / "SOUL.md").write_bytes(PROSE["SOUL.md"])
    (staging / attest.FILE).write_text(json.dumps(att))
    backup = store / f".{hk}.old"
    backup.mkdir()
    (backup / "SOUL.md").write_text("the crown it was replacing\n")

    b = o._incumbent_bundle(_cfg(tmp_path, repo), "HEAD", hk, tmp_path / "staged", incumbents=store)
    assert b and not b["problems"] and b["digest"] == digest
    assert (store / hk / "SOUL.md").read_bytes() == PROSE["SOUL.md"]
    assert not staging.exists() and not backup.exists()


def test_a_staging_dir_beside_a_live_crown_is_dropped_not_published(tmp_path, monkeypatch):
    """A scratch directory is not a marker's orphan. Releasing it would publish a second copy of a bundle that
    is still defending, under a name the commitment does not use."""
    repo, kp = _repo(tmp_path), _kp()
    hk = kp.ss58_address
    cfg = _cfg(tmp_path, repo)
    rd = tmp_path / "rd"
    rd.mkdir()
    store = cfg.state / "incumbents"
    live = store / hk
    live.mkdir(parents=True)
    (live / "SOUL.md").write_text("the crown\n")
    staging = store / f".{hk}.new"
    staging.mkdir()
    (staging / "SOUL.md").write_text("half written, not the crown\n")

    monkeypatch.setattr(o, "sh", lambda *_a, **_k: f"submissions/{hk}\n")
    assert o._prune_orphan_incumbents(cfg, rd) == []
    assert (live / "SOUL.md").read_text() == "the crown\n"
    assert not staging.exists()
    assert not (rd / "reveal").exists()


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").strip()


def test_private_only_seals_an_attestation_only_pr_from_the_store(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    base = _head(repo)
    ref = _commit_submission(repo, hk, _attestation_only(att))
    store = _store(tmp_path, hk, att, PROSE)
    b = o._reveal_challenger(
        _cfg(tmp_path, repo), ref, hk, tmp_path / "staged", round_id="r0001", store=store, base=base, private_only=True
    )
    assert b and not b["problems"] and b["digest"] == digest


def test_private_only_refuses_a_pr_that_carries_its_prose(tmp_path):
    """The prose in the PR is public the moment it is opened. Even with the bundle uploaded, the PR is refused."""
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    base = _head(repo)
    ref = _commit_submission(repo, hk, {**PROSE, **_attestation_only(att)})
    store = _store(tmp_path, hk, att, PROSE)
    b = o._reveal_challenger(
        _cfg(tmp_path, repo), ref, hk, tmp_path / "staged", round_id="r0001", store=store, base=base, private_only=True
    )
    assert b["problems"] and "carries strategy files (SOUL.md)" in b["problems"][0]


def test_private_only_never_falls_back_to_the_tree(tmp_path):
    """A king whose old prose is already public on the branch resubmits with a commitment alone. The files it did
    not add are not held against it — and without an upload the old prose in the tree is not used either."""
    repo, kp = _repo(tmp_path), _kp()
    hk = kp.ss58_address
    old = {"SOUL.md": b"# Soul\n\nThe crown's old, already public prose.\n"}
    _commit_submission(repo, hk, {**old, **_attestation_only(attest.sign(kp, "r0000", bundle_digest(old)))})
    base = _head(repo)
    att = attest.sign(kp, "r0001", bundle_digest(PROSE))
    (repo / "submissions" / hk / attest.FILE).write_text(json.dumps(att) + "\n")  # the PR changes only this
    _git(repo, "commit", "-qam", "resubmit")
    ref, cfg = _head(repo), _cfg(tmp_path, repo)
    b = o._reveal_challenger(
        cfg, ref, hk, tmp_path / "staged", round_id="r0001", store=tmp_path / "empty", base=base, private_only=True
    )
    assert b["problems"] and "no revealed bundle" in b["problems"][0]
    store = _store(tmp_path, hk, att, PROSE)
    b = o._reveal_challenger(
        cfg, ref, hk, tmp_path / "staged2", round_id="r0001", store=store, base=base, private_only=True
    )
    assert b and not b["problems"] and b["digest"] == bundle_digest(PROSE)


def test_private_only_rejects_a_pr_it_cannot_diff_without_raising(tmp_path):
    """One PR whose diff does not run is refused; it must not stop the seal for everyone else."""
    repo, kp = _repo(tmp_path), _kp()
    hk = kp.ss58_address
    att = attest.sign(kp, "r0001", bundle_digest(PROSE))
    ref = _commit_submission(repo, hk, _attestation_only(att))
    b = o._reveal_challenger(
        _cfg(tmp_path, repo),
        ref,
        hk,
        tmp_path / "staged",
        round_id="r0001",
        store=_store(tmp_path, hk, att, PROSE),
        base="no-such-ref",
        private_only=True,
    )
    assert b["problems"] and "could not be compared" in b["problems"][0]


def test_without_a_server_a_prose_pr_still_seals_from_its_tree(tmp_path):
    repo, kp = _repo(tmp_path), _kp()
    hk, digest = kp.ss58_address, bundle_digest(PROSE)
    att = attest.sign(kp, "r0001", digest)
    base = _head(repo)
    ref = _commit_submission(repo, hk, {**PROSE, **_attestation_only(att)})
    b = o._reveal_challenger(
        _cfg(tmp_path, repo), ref, hk, tmp_path / "staged", round_id="r0001", store=tmp_path / "e", base=base
    )
    assert b and not b["problems"] and b["digest"] == digest


def test_a_failed_fetch_is_not_a_crown_that_failed_to_land(tmp_path):
    """The retain reads origin/main. A fetch that does not run must raise, so the round retries, rather than
    looking like the marker is gone and dropping the king. A fetch that works and finds no directory is real."""
    repo = _repo(tmp_path)
    hk = "5C" + "o" * 46
    _commit_submission(repo, hk, {"SOUL.md": b"# Soul\n"})
    _git(repo, "branch", "-M", "main")
    bare = tmp_path / "origin.git"
    _git(repo, "clone", "--bare", "-q", str(repo), str(bare))
    _git(repo, "remote", "add", "origin", str(bare))
    cfg = _cfg(tmp_path, repo)
    assert o._crown_landed(cfg, hk) is True
    assert o._crown_landed(cfg, f"{hk}x") is False
    _git(repo, "remote", "set-url", "origin", str(tmp_path / "no-such.git"))
    with pytest.raises(RuntimeError):
        o._crown_landed(cfg, hk)
