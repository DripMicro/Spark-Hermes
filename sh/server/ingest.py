"""Private submission ingestion — the *reveal* channel of the commit–reveal scheme (Phase 1).

A strategy is submitted in two halves. The **commit** is a public GitHub PR carrying only
`attestation.json`: the hotkey's sr25519 signature over the round and the bundle's digest. The
**reveal** — the prose bundle itself — is uploaded here, privately, so a later miner in the same
window cannot read it. The seal reads the revealed bundle from this store by the digest the public
attestation committed to; the bundle is made public only after the round is scored (a challenger at
its round's close, the king only when it is dethroned).

This server runs on the validator host, beside the round state (`$SH_STATE/rounds/<round>/`), and
never on the GPU worker. It reuses the exact lint, attestation and answer-copy (S1) code the seal
uses, so a bundle that would be rejected at the seal is rejected here first, with the same words —
and the digest, which every commitment is made over, is computed by the one frozen function.

    python -m sh.server.ingest --state ~/.spark-hermes-state --gate allowlist --port 8091

Endpoints (all uploads are signature-gated by the hotkey; nothing returns another miner's prose):
    POST /submit    {"attestation": {...}, "files": {"<path>": "<base64>"}}   -> receipt | problems
    GET  /status    ?hotkey=<ss58>[&round=<rNNNN>]                            -> the owner's verdict
    GET  /healthz                                                             -> {"ok": true, "round": ...}
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import shutil
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from sh.cli import attest
from sh.cli.lint import bundle_digest, lint
from sh.validator import similarity

FUTURE_SLACK_S = 600  # a signing time this far ahead is not a submission (mirrors the seal's one_per_hotkey)
Gate = Callable[[str], bool]


def _read(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text()) if path.exists() else default


def _reject(problems: list[str], code: str = "invalid") -> dict:
    return {"ok": False, "code": code, "problems": problems}


# ─── round state the server reads (authoritative: the same files the loop wrote) ──────────────────
def current_round(state: Path) -> str | None:
    """The round accepting submissions now: the latest round directory without a DONE marker."""
    rounds = sorted(p for p in (state / "rounds").glob("r*") if p.is_dir()) if (state / "rounds").exists() else []
    for rd in reversed(rounds):
        if not (rd / "DONE").exists():
            return rd.name
    return None


def window_open(state: Path, round_id: str, now: float) -> bool:
    w = _read(state / "rounds" / round_id / "window.json")
    return bool(w) and now < w.get("closes_at", 0)


# ─── validation (pure but for reading the round's references; no writes) ──────────────────────────
def validate(payload: dict, *, round_id: str, round_dir: Path, is_registered: Gate, now: float) -> dict:
    """Everything the seal checks, checked here at upload: the attestation binds this hotkey to this
    round and this digest and verifies; the prose passes the lint; the bundle does not reproduce the
    round's answers (S1). Returns the accepted upload, or the refusal with the seal's own wording."""
    att = payload.get("attestation")
    raw_files = payload.get("files")
    if not isinstance(att, dict) or not isinstance(raw_files, dict):
        return _reject(["body must be {attestation: {...}, files: {path: base64}}"])
    if att.get("round_id") != round_id:
        return _reject([f"signed for {att.get('round_id')!r}, the open round is {round_id!r}"], code="wrong_round")
    hotkey = str(att.get("hotkey", ""))
    if not attest.SS58.match(hotkey):
        return _reject(["attestation hotkey is not an ss58 address"])
    if not is_registered(hotkey):
        return _reject([f"hotkey {hotkey} is not registered on SN74"], code="not_registered")
    try:
        files = {p: base64.b64decode(b) for p, b in raw_files.items()}
    except (ValueError, TypeError):
        return _reject(["files are not valid base64"])
    files.pop(attest.FILE, None)  # the attestation travels in `attestation`, never as a bundle file
    digest = bundle_digest(files)
    problems = lint(files) + attest.problems(att, digest=digest, round_id=round_id)
    if problems:
        return _reject(problems, code="lint")
    if att["signed_at"] > now + FUTURE_SLACK_S:
        return _reject(["signed_at is in the future"])
    answers = similarity.load(round_dir)
    if answers and (why := answers.refuse(similarity.bundle_text(files))):
        return _reject([why], code="s1")
    return {"ok": True, "hotkey": hotkey, "digest": digest, "signed_at": int(att["signed_at"]), "files": files, "attestation": att}


# ─── storage + receipt ────────────────────────────────────────────────────────────────────────────
def _receipt(round_id: str, hotkey: str, digest: str, signed_at: int, now: float, secret: bytes | None) -> dict:
    r = {
        "schema": "sh-receipt-v1",
        "round_id": round_id,
        "hotkey": hotkey,
        "digest": digest,
        "signed_at": signed_at,
        "received_at": int(now),
        "lint_ok": True,
        "s1_ok": True,
    }
    if secret:  # a server signature the miner (and, in a dispute, the validator) can check — not consensus, evidence
        body = f"{round_id}:{hotkey}:{digest}:{signed_at}:{r['received_at']}".encode()
        r["server_sig"] = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return r


def _update_index(store: Path, round_id: str, hotkey: str, digest: str, signed_at: int, now: float) -> None:
    """A convenience pointer to each hotkey's latest signed upload for `/status`. The seal is
    authoritative — it picks the latest signed PR and fetches *that* digest — so this only advises."""
    path = store / round_id / "index.json"
    idx = _read(path, {})
    cur = idx.get(hotkey)
    newer = cur is None or signed_at > cur["signed_at"] or (signed_at == cur["signed_at"] and digest > cur["digest"])
    if newer:
        idx[hotkey] = {"digest": digest, "signed_at": signed_at, "received_at": int(now)}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(idx, indent=1))


def store_upload(result: dict, *, store: Path, round_id: str, now: float, secret: bytes | None) -> dict:
    """Persist an accepted upload under `<round>/<hotkey>/uploads/<signed_at>-<digest>/`. Idempotent:
    re-uploading the same digest is a no-op. Every upload is kept; the seal reads the one its chosen
    PR committed to. Written to a temp dir and renamed so a crash never leaves a half-written bundle."""
    hotkey, digest, signed_at = result["hotkey"], result["digest"], result["signed_at"]
    receipt = _receipt(round_id, hotkey, digest, signed_at, now, secret)
    dest = store / round_id / hotkey / "uploads" / f"{signed_at}-{digest}"
    if dest.exists():
        return receipt
    tmp = dest.with_name(dest.name + ".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    for rel, data in result["files"].items():
        f = tmp / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
    (tmp / attest.FILE).write_text(json.dumps(result["attestation"], indent=1) + "\n")
    (tmp / "receipt.json").write_text(json.dumps(receipt, indent=1) + "\n")
    tmp.rename(dest)
    _update_index(store, round_id, hotkey, digest, signed_at, now)
    return receipt


def ingest(payload: dict, *, state: Path, store: Path, is_registered: Gate, now: float, secret: bytes | None) -> dict:
    """One upload, end to end: refuse unless a window is open, validate, then store. Pure of the HTTP layer."""
    round_id = current_round(state)
    if round_id is None:
        return _reject(["no round is open"], code="closed")
    if not window_open(state, round_id, now):
        return _reject([f"the submission window for {round_id} is not open"], code="closed")
    result = validate(payload, round_id=round_id, round_dir=state / "rounds" / round_id, is_registered=is_registered, now=now)
    if not result["ok"]:
        return result
    return {"ok": True, "receipt": store_upload(result, store=store, round_id=round_id, now=now, secret=secret)}


def status(state: Path, store: Path, *, hotkey: str, round_id: str | None = None) -> dict:
    """The owner's own verdict for their latest upload — metadata only, never prose. The digest is
    already public in the PR, so this leaks nothing a reader could not already see."""
    round_id = round_id or current_round(state)
    entry = _read(store / round_id / "index.json", {}).get(hotkey) if round_id else None
    return {"round_id": round_id, "hotkey": hotkey, "has_upload": bool(entry), **(entry or {})}


# ─── registration gates ───────────────────────────────────────────────────────────────────────────
def allow_all(_hotkey: str) -> bool:  # tests, or a deliberately open deployment
    return True


def allowlist_gate(path: Path) -> Gate:
    """Registered hotkeys, one ss58 per line. Re-read per call so the list can be edited live."""
    def gate(hotkey: str) -> bool:
        try:
            return hotkey in {ln.strip() for ln in path.read_text().splitlines() if ln.strip()}
        except OSError:
            return False

    return gate


def metagraph_gate(_netuid: int, _network: str) -> Gate:  # TODO(phase-1-ops): wire the live SN74 metagraph
    raise NotImplementedError(
        "the live metagraph gate is not wired yet (needs the netuid and a metagraph reader); "
        "use --gate allowlist or --gate none for now"
    )


# ─── HTTP layer ───────────────────────────────────────────────────────────────────────────────────
class _RateLimiter:
    """Best-effort, in-memory: per-hotkey and global upload caps within the current window. Resets on
    restart — a durable cap can replace it later; this only blunts a flood, it is not the Sybil gate."""

    def __init__(self, per_hotkey: int, total: int) -> None:
        self.per_hotkey, self.total = per_hotkey, total
        self._by: dict[tuple[str, str], int] = {}
        self._total: dict[str, int] = {}
        self._lock = threading.Lock()

    def allow(self, round_id: str, hotkey: str) -> bool:
        with self._lock:
            if self._total.get(round_id, 0) >= self.total:
                return False
            if self._by.get((round_id, hotkey), 0) >= self.per_hotkey:
                return False
            self._by[(round_id, hotkey)] = self._by.get((round_id, hotkey), 0) + 1
            self._total[round_id] = self._total.get(round_id, 0) + 1
            return True


def make_handler(*, state: Path, store: Path, gate: Gate, secret: bytes | None, limiter: _RateLimiter):
    class Handler(BaseHTTPRequestHandler):
        server_version = "sh-ingest/1"

        def _send(self, code: int, body: dict) -> None:
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args) -> None:  # quiet by default; the loop's board is the operator view
            pass

        def do_GET(self) -> None:
            u = urlparse(self.path)
            if u.path == "/healthz":
                self._send(200, {"ok": True, "round": current_round(state)})
                return
            if u.path == "/status":
                q = parse_qs(u.query)
                hotkey = (q.get("hotkey") or [""])[0]
                if not attest.SS58.match(hotkey):
                    self._send(400, {"ok": False, "problems": ["hotkey query is not an ss58 address"]})
                    return
                self._send(200, {"ok": True, **status(state, store, hotkey=hotkey, round_id=(q.get("round") or [None])[0])})
                return
            self._send(404, {"ok": False, "problems": ["not found"]})

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/submit":
                self._send(404, {"ok": False, "problems": ["not found"]})
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > 2 * 1024 * 1024:  # a bundle is <=512 KiB; base64 inflates ~4/3
                self._send(413, {"ok": False, "problems": ["missing or oversized body"]})
                return
            try:
                payload = json.loads(self.rfile.read(length))
            except (ValueError, UnicodeDecodeError):
                self._send(400, {"ok": False, "problems": ["body is not JSON"]})
                return
            hotkey = (payload.get("attestation") or {}).get("hotkey") if isinstance(payload, dict) else None
            rid = current_round(state)
            if rid and attest.SS58.match(str(hotkey or "")) and not limiter.allow(rid, str(hotkey)):
                self._send(429, {"ok": False, "code": "rate_limited", "problems": ["too many uploads this window"]})
                return
            result = ingest(payload if isinstance(payload, dict) else {}, state=state, store=store,
                            is_registered=gate, now=time.time(), secret=secret)
            self._send(200 if result["ok"] else 400, result)

    return Handler


def build_gate(kind: str, allowlist: Path | None, netuid: int, network: str) -> Gate:
    if kind == "none":
        return allow_all
    if kind == "allowlist":
        if not allowlist:
            raise SystemExit("--gate allowlist needs --allowlist PATH")
        return allowlist_gate(allowlist)
    if kind == "metagraph":
        return metagraph_gate(netuid, network)
    raise SystemExit(f"unknown --gate {kind!r}")


def main(argv=None) -> int:
    import os

    ap = argparse.ArgumentParser(description="Spark-Hermes private submission ingestion")
    ap.add_argument("--state", default=os.environ.get("SH_STATE", str(Path.home() / ".spark-hermes-state")))
    ap.add_argument("--store", help="where uploads are kept (default: $SH_STATE/submissions)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8091)
    ap.add_argument("--gate", choices=("none", "allowlist", "metagraph"), default="allowlist")
    ap.add_argument("--allowlist", help="ss58-per-line file of registered hotkeys (for --gate allowlist)")
    ap.add_argument("--netuid", type=int, default=74)
    ap.add_argument("--network", default="finney")
    ap.add_argument("--secret-file", help="HMAC key for receipts (default: $SH_STATE/server_secret if present)")
    ap.add_argument("--max-per-hotkey", type=int, default=200, help="upload cap per hotkey per window")
    ap.add_argument("--max-total", type=int, default=5000, help="upload cap across all hotkeys per window")
    a = ap.parse_args(argv)

    state = Path(a.state)
    store = Path(a.store) if a.store else state / "submissions"
    store.mkdir(parents=True, exist_ok=True)
    secret_path = Path(a.secret_file) if a.secret_file else state / "server_secret"
    secret = secret_path.read_bytes().strip() if secret_path.exists() else None
    if secret is None:
        print(f"[ingest] no receipt secret at {secret_path}; receipts will be unsigned", file=sys.stderr)
    gate = build_gate(a.gate, Path(a.allowlist) if a.allowlist else None, a.netuid, a.network)
    handler = make_handler(state=state, store=store, gate=gate,
                           secret=secret, limiter=_RateLimiter(a.max_per_hotkey, a.max_total))
    httpd = ThreadingHTTPServer((a.host, a.port), handler)
    print(f"[ingest] {a.host}:{a.port} state={state} store={store} gate={a.gate} round={current_round(state)}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
