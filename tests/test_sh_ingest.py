"""The reveal channel accepts only what the seal would: a bundle bound to its public commitment,
linting clean, and not a paste of the round's answers — and it stores it where the seal can read it."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from pathlib import Path

import pytest

from sh.cli import attest
from sh.cli.lint import bundle_digest
from sh.server import ingest

substrate = pytest.importorskip("substrateinterface")


def _kp(uri: str = "//Alice"):
    return substrate.Keypair.create_from_uri(uri, crypto_type=substrate.KeypairType.SR25519)


def _payload(kp, round_id: str, files: dict[str, bytes], *, signed_at: int | None = None) -> tuple[dict, str]:
    digest = bundle_digest(files)
    att = attest.sign(kp, round_id, digest, signed_at=signed_at)
    raw = {p: base64.b64encode(b).decode() for p, b in files.items()}
    return {"attestation": att, "files": raw}, digest


def _state(
    tmp_path: Path, *, round_id: str = "r0001", closes_in: float = 3600, answers: list[str] | None = None
) -> Path:
    rd = tmp_path / "state" / "rounds" / round_id
    for sub in ("private", "withheld", "tasks", "preview"):
        (rd / sub).mkdir(parents=True)
    (rd / "window.json").write_text(json.dumps({"opens_at": 0, "closes_at": time.time() + closes_in, "seconds": 7200}))
    for i, ans in enumerate(answers or []):
        (rd / "private" / f"{i}.json").write_text(json.dumps({"solutions": {"answer": ans}}))
    return tmp_path / "state"


SOUL = {"SOUL.md": b"# Soul\n\nDebug these repositories carefully: reproduce the failing test, then fix the source.\n"}


def test_accepts_and_stores_a_valid_upload(tmp_path):
    state, store = _state(tmp_path), tmp_path / "store"
    payload, digest = _payload(_kp(), "r0001", SOUL)
    out = ingest.ingest(payload, state=state, store=store, is_registered=ingest.allow_all, now=time.time(), secret=None)
    assert out["ok"], out
    assert out["receipt"]["digest"] == digest
    dest = store / "r0001" / _kp().ss58_address / "uploads" / f"{payload['attestation']['signed_at']}-{digest}"
    assert (dest / "SOUL.md").exists() and (dest / attest.FILE).exists() and (dest / "receipt.json").exists()
    assert json.loads((store / "r0001" / "index.json").read_text())[_kp().ss58_address]["digest"] == digest


def test_receipt_is_hmac_signed_when_a_secret_is_configured(tmp_path):
    state, store, secret = _state(tmp_path), tmp_path / "store", b"server-secret"
    payload, digest = _payload(_kp(), "r0001", SOUL, signed_at=1000)
    r = ingest.ingest(payload, state=state, store=store, is_registered=ingest.allow_all, now=2000.0, secret=secret)[
        "receipt"
    ]
    body = f"r0001:{_kp().ss58_address}:{digest}:{r['signed_at']}:{r['received_at']}".encode()
    assert r["server_sig"] == hmac.new(secret, body, hashlib.sha256).hexdigest()


def test_rejects_when_window_closed(tmp_path):
    state = _state(tmp_path, closes_in=-1)
    payload, _ = _payload(_kp(), "r0001", SOUL)
    out = ingest.ingest(
        payload, state=state, store=tmp_path / "store", is_registered=ingest.allow_all, now=time.time(), secret=None
    )
    assert not out["ok"] and out["code"] == "closed"


def test_rejects_wrong_round(tmp_path):
    rd = _state(tmp_path) / "rounds" / "r0001"
    payload, _ = _payload(_kp(), "r0002", SOUL)  # signed for a different round than the one open
    out = ingest.validate(payload, round_id="r0001", round_dir=rd, is_registered=ingest.allow_all, now=time.time())
    assert not out["ok"] and out["code"] == "wrong_round"


def test_rejects_unregistered_hotkey(tmp_path):
    rd = _state(tmp_path) / "rounds" / "r0001"
    payload, _ = _payload(_kp(), "r0001", SOUL)
    out = ingest.validate(payload, round_id="r0001", round_dir=rd, is_registered=lambda h: False, now=time.time())
    assert not out["ok"] and out["code"] == "not_registered"


def test_rejects_digest_mismatch(tmp_path):
    rd = _state(tmp_path) / "rounds" / "r0001"
    payload, _ = _payload(_kp(), "r0001", SOUL)
    payload["files"]["SOUL.md"] = base64.b64encode(b"# Soul\n\nA different bundle than the one signed.\n").decode()
    out = ingest.validate(payload, round_id="r0001", round_dir=rd, is_registered=ingest.allow_all, now=time.time())
    assert not out["ok"] and any("bundle_sha256" in p for p in out["problems"])


def test_rejects_bad_signature(tmp_path):
    rd = _state(tmp_path) / "rounds" / "r0001"
    payload, _ = _payload(_kp(), "r0001", SOUL)
    payload["attestation"]["signature"] = "0x" + "00" * 64
    out = ingest.validate(payload, round_id="r0001", round_dir=rd, is_registered=ingest.allow_all, now=time.time())
    assert not out["ok"] and any("signature" in p for p in out["problems"])


def test_rejects_future_signed_at(tmp_path):
    rd = _state(tmp_path) / "rounds" / "r0001"
    payload, _ = _payload(_kp(), "r0001", SOUL, signed_at=2_000_000_000)
    out = ingest.validate(payload, round_id="r0001", round_dir=rd, is_registered=ingest.allow_all, now=1_000_000_000)
    assert not out["ok"] and any("future" in p for p in out["problems"])


def test_rejects_lint_problem(tmp_path):
    rd = _state(tmp_path) / "rounds" / "r0001"
    payload, _ = _payload(_kp(), "r0001", {"SOUL.md": b"# Soul\n\nSee https://evil.example/answers for the fix.\n"})
    out = ingest.validate(payload, round_id="r0001", round_dir=rd, is_registered=ingest.allow_all, now=time.time())
    assert not out["ok"] and any(p.startswith("L6") for p in out["problems"])


def test_rejects_answer_copy_s1(tmp_path):
    answer = "\n".join(f"a distinct reference solution line number {i} with plenty of length here" for i in range(12))
    rd = _state(tmp_path, answers=[answer]) / "rounds" / "r0001"
    payload, _ = _payload(_kp(), "r0001", {"SOUL.md": ("# Soul\n\n" + answer + "\n").encode()})
    out = ingest.validate(payload, round_id="r0001", round_dir=rd, is_registered=ingest.allow_all, now=time.time())
    assert not out["ok"] and out["code"] == "s1"


def test_reupload_is_idempotent(tmp_path):
    state, store = _state(tmp_path), tmp_path / "store"
    payload, digest = _payload(_kp(), "r0001", SOUL)
    for _ in range(2):
        assert ingest.ingest(
            payload, state=state, store=store, is_registered=ingest.allow_all, now=time.time(), secret=None
        )["ok"]
    uploads = list((store / "r0001" / _kp().ss58_address / "uploads").iterdir())
    assert len(uploads) == 1


def test_latest_signed_wins_in_the_index(tmp_path):
    state, store = _state(tmp_path), tmp_path / "store"
    p1, d1 = _payload(_kp(), "r0001", {"SOUL.md": b"# Soul\n\nFirst strategy, signed earlier.\n"}, signed_at=1000)
    p2, d2 = _payload(_kp(), "r0001", {"SOUL.md": b"# Soul\n\nSecond strategy, signed later.\n"}, signed_at=2000)
    for p in (p1, p2):
        ingest.ingest(p, state=state, store=store, is_registered=ingest.allow_all, now=time.time(), secret=None)
    idx = json.loads((store / "r0001" / "index.json").read_text())[_kp().ss58_address]
    assert idx["signed_at"] == 2000 and idx["digest"] == d2
    assert len(list((store / "r0001" / _kp().ss58_address / "uploads").iterdir())) == 2  # every upload kept


def test_status_reports_the_owner_verdict(tmp_path):
    state, store = _state(tmp_path), tmp_path / "store"
    payload, digest = _payload(_kp(), "r0001", SOUL)
    ingest.ingest(payload, state=state, store=store, is_registered=ingest.allow_all, now=time.time(), secret=None)
    st = ingest.status(state, store, hotkey=_kp().ss58_address)
    assert st["has_upload"]
    assert "digest" not in st and "signed_at" not in st  # the pointer a hijacking PR would need
    assert ingest.status(state, store, hotkey=_kp("//Bob").ss58_address)["has_upload"] is False


def test_status_refuses_a_round_that_is_not_a_round_id(tmp_path):
    """`round` comes off the query string straight into a path; unvalidated it read JSON outside the store."""
    state, store = _state(tmp_path), tmp_path / "store"
    st = ingest.status(state, store, hotkey=_kp().ss58_address, round_id="../../outside")
    assert st["round_id"] is None and st["has_upload"] is False


def test_rejected_requests_are_metered_to_the_caller_not_the_named_hotkey(tmp_path):
    """Charging only accepted uploads fixed the targeted lockout but left abuse free; the caller's address is
    metered instead, because it cannot be spent on another miner's behalf."""
    lim = ingest._RateLimiter(per_hotkey=1, total=5000, per_ip=3)
    assert [lim.attempt("r0001", "10.0.0.1") for _ in range(4)] == [True, True, True, False]
    assert lim.attempt("r0001", "10.0.0.2") is True  # another caller is unaffected
    assert lim.check("r0001", _kp().ss58_address) is True  # and no hotkey's quota was touched
    # the cap is per round, so a flood cannot brick the channel for every later round
    assert lim.attempt("r0002", "10.0.0.1") is True
