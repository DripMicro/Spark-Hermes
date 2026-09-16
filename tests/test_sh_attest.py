"""A PR belongs to a hotkey and to a round because the hotkey signed that round's digest — nothing else."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sh.cli import attest
from sh.cli.lint import bundle_digest, check

substrate = pytest.importorskip("substrateinterface")


def _bundle(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return root


def _kp():
    return substrate.Keypair.create_from_uri("//Alice", crypto_type=substrate.KeypairType.SR25519)


def test_a_signed_bundle_verifies_for_its_hotkey_and_round(tmp_path):
    kp = _kp()
    root = _bundle(tmp_path / "b", {"SOUL.md": "Be careful.\n"})
    digest = bundle_digest({"SOUL.md": b"Be careful.\n"})
    (root / attest.FILE).write_text(json.dumps(attest.sign(kp, "r0007", digest)))
    r = check(root, hotkey=kp.ss58_address, round_id="r0007", require_attestation=True)
    assert r["ok"], r["problems"]
    assert r["bundle_sha256"] == digest  # the attestation is outside the digest
    assert r["attestation"] == {"hotkey": kp.ss58_address, "round_id": "r0007", "verified": True}


def test_the_attestation_binds_the_round_the_digest_and_the_directory(tmp_path):
    kp = _kp()
    root = _bundle(tmp_path / "b", {"SOUL.md": "Be careful.\n"})
    digest = bundle_digest({"SOUL.md": b"Be careful.\n"})
    (root / attest.FILE).write_text(json.dumps(attest.sign(kp, "r0007", digest)))
    assert any("signed for r0007, this round is r0008" in p for p in check(root, round_id="r0008")["problems"])
    assert any("!= submission directory" in p for p in check(root, hotkey="5Fother")["problems"])
    (root / "SOUL.md").write_text("Be bold.\n")  # edited after signing
    assert any("does not match the bundle" in p for p in check(root)["problems"])


def test_a_forged_signature_is_refused(tmp_path):
    kp, other = _kp(), substrate.Keypair.create_from_uri("//Bob", crypto_type=substrate.KeypairType.SR25519)
    root = _bundle(tmp_path / "b", {"SOUL.md": "Be careful.\n"})
    digest = bundle_digest({"SOUL.md": b"Be careful.\n"})
    att = attest.sign(other, "r0007", digest)
    att["hotkey"] = kp.ss58_address  # Bob signs, claims to be Alice
    (root / attest.FILE).write_text(json.dumps(att))
    assert any("signature is not the hotkey's" in p for p in check(root)["problems"])


def test_a_bundle_without_attestation_lints_but_cannot_be_sealed(tmp_path):
    root = _bundle(tmp_path / "b", {"SOUL.md": "Be careful.\n"})
    assert check(root)["ok"]
    assert any(p.startswith("L10") and "missing" in p for p in check(root, require_attestation=True)["problems"])


def test_keypair_loads_from_a_bittensor_hotkey_file(tmp_path):
    mnemonic = substrate.Keypair.generate_mnemonic()
    kp = substrate.Keypair.create_from_mnemonic(mnemonic, crypto_type=substrate.KeypairType.SR25519)
    seed = kp.seed_hex if isinstance(kp.seed_hex, str) else "0x" + bytes(kp.seed_hex).hex()
    f = tmp_path / "hotkey"
    f.write_text(json.dumps({"secretSeed": seed, "secretPhrase": mnemonic, "ss58Address": kp.ss58_address}))
    assert attest.load_keypair(str(f)).ss58_address == kp.ss58_address
    (tmp_path / "phrase").write_text(json.dumps({"secretPhrase": mnemonic}))
    assert attest.load_keypair(str(tmp_path / "phrase")).ss58_address == kp.ss58_address
    assert attest.load_keypair("//Alice").ss58_address == _kp().ss58_address
