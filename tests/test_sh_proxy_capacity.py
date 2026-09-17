"""The proxy on one GPU: the pinned sampling is its own default, a refused call is held rather than failed, and an
episode's token budget ends it cleanly."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import sh.validator.proxy as P


def _engine(script):
    """A fake engine answering POSTs from `script`: a list of (status, body) consumed in order."""
    seen = []

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            seen.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            status, body = script.pop(0) if script else (200, {"usage": {"prompt_tokens": 1, "completion_tokens": 1}})
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, seen


def _proxy(tmp_path, upstream):
    tokens = P.Tokens(tmp_path / "tokens")
    srv = P.serve("127.0.0.1:0", upstream, tmp_path / "tokens", tmp_path / "usage", P.PINNED_SAMPLING)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, tokens


def _post(port, token, body=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/v1/chat/completions",
        data=json.dumps(body or {"messages": [], "temperature": 0.0}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_the_pinned_sampling_is_the_proxys_own_default_and_overrides_the_request(tmp_path):
    """A proxy started without --sampling ran r0003–r0004 at the retired temperature 0.2."""
    pins = (__import__("pathlib").Path(__file__).parents[1] / "docs" / "pins.md").read_text()
    assert P.PINNED_SAMPLING == {"temperature": 0.7, "top_p": 0.95, "max_tokens": 8192}
    assert "`temperature 0.7`**, `top_p 0.95`, `max_tokens 8192`" in pins
    engine, seen = _engine([])
    proxy, tokens = _proxy(tmp_path, f"http://127.0.0.1:{engine.server_address[1]}")
    status, _ = _post(proxy.server_address[1], tokens.issue("ep-1", ttl=60))
    assert status == 200 and seen[0]["temperature"] == 0.7 and seen[0]["top_p"] == 0.95


def test_a_call_the_engine_refuses_for_capacity_is_held_and_retried_not_failed(tmp_path, monkeypatch):
    monkeypatch.setattr(P.time, "sleep", lambda s: None)
    engine, seen = _engine(
        [
            (503, {"error": "server overloaded: no capacity for this request right now"}),
            (503, {"error": "server overloaded: no capacity for this request right now"}),
            (200, {"usage": {"prompt_tokens": 100, "completion_tokens": 5}}),
        ]
    )
    proxy, tokens = _proxy(tmp_path, f"http://127.0.0.1:{engine.server_address[1]}")
    status, body = _post(proxy.server_address[1], tokens.issue("ep-2", ttl=60))
    assert status == 200 and len(seen) == 3
    row = json.loads((tmp_path / "usage" / "ep-2.jsonl").read_text().splitlines()[0])
    assert row["usage"]["prompt_tokens"] == 100 and "queued_s" in row


def test_an_ordinary_client_error_is_passed_through_at_once(tmp_path, monkeypatch):
    monkeypatch.setattr(P.time, "sleep", lambda s: (_ for _ in ()).throw(AssertionError("must not wait")))
    engine, seen = _engine([(400, {"error": "bad request: messages is empty"})])
    proxy, tokens = _proxy(tmp_path, f"http://127.0.0.1:{engine.server_address[1]}")
    status, _ = _post(proxy.server_address[1], tokens.issue("ep-3", ttl=60))
    assert status == 400 and len(seen) == 1


def test_a_spent_token_budget_ends_the_episode_with_a_402_and_a_marker(tmp_path):
    engine, seen = _engine([(200, {"usage": {"prompt_tokens": 900, "completion_tokens": 150}})])
    proxy, tokens = _proxy(tmp_path, f"http://127.0.0.1:{engine.server_address[1]}")
    tok = tokens.issue("ep-4", ttl=60, budget=1000)
    assert _post(proxy.server_address[1], tok)[0] == 200  # 0 spent: forwarded, 1050 recorded
    status, body = _post(proxy.server_address[1], tok)
    assert status == 402 and "budget spent" in body["error"]["message"] and len(seen) == 1
    marks = [json.loads(line) for line in (tmp_path / "usage" / "ep-4.jsonl").read_text().splitlines()]
    assert marks[-1]["budget_spent"] == {"spent": 1050, "budget": 1000}
    assert tokens.issue("ep-5", ttl=60) and _post(proxy.server_address[1], tokens.issue("ep-5", ttl=60))[0] == 200


def test_a_spent_budget_is_an_ending_never_a_void(monkeypatch, tmp_path):
    import sh.validator.grade as g

    (tmp_path / "result.json").write_text(
        json.dumps({"messages": [], "failed": True, "failure_reason": "billing", "failure_retryable": False})
    )
    (tmp_path / "finish.json").write_text(
        json.dumps({"api_calls": 40, "wall_s": 900.0, "budget_spent": {"spent": 612000, "budget": 600000}})
    )
    monkeypatch.setattr(g, "grade_in_container", lambda *a, **k: {"published_pass": True, "protected_modified": []})
    rec = g.grade(tmp_path, {"task_id": "t-1", "published": {"predicates": []}}, None, "img")
    assert not rec["void"] and "token_budget_spent" in rec["signals"] and rec["budget_spent"]["budget"] == 600000
