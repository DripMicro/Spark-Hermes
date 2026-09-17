"""`custom facet_test:<id>` — one predicate per verifier test case. Runs inside the grading container: the test
file arrives in `/ep/withheld.json` under `assets` (never in the agent's boundary), pytest runs once per
workspace on the image's system interpreter, and each predicate reads its own outcome from the junit report."""

import base64
import json
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET

_RESULTS: dict = {}


def _run_tests(ws) -> dict:
    key = str(ws)
    if key in _RESULTS:
        return _RESULTS[key]
    ep = os.environ.get("SH_EP", "/ep")
    assets = {}
    try:
        assets = json.load(open(os.path.join(ep, "withheld.json"))).get("assets", {})
    except (OSError, ValueError):
        pass
    d = tempfile.mkdtemp(prefix="sh-tests-")
    for rel, b64 in assets.items():
        p = os.path.join(d, os.path.basename(rel))
        with open(p, "wb") as f:
            f.write(base64.b64decode(b64))
    report = os.path.join(d, "junit.xml")
    env = {**os.environ, "HOME": d, "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        subprocess.run(
            ["/usr/bin/python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml", report, os.path.join(d, "test_state.py")],
            cwd=str(ws), env=env, capture_output=True, timeout=300,
        )
    except subprocess.TimeoutExpired:
        pass
    results = {}
    try:
        for case in ET.parse(report).getroot().iter("testcase"):
            parts = (case.get("classname") or "").split(".")[1:]  # module.Class... -> Class...
            node = "::".join(["test_state.py", *parts, case.get("name") or ""])
            results[node] = not any(c.tag in ("failure", "error", "skipped") for c in case)
    except (OSError, ET.ParseError):
        pass
    _RESULTS[key] = results
    return results


def facet_test(ws, node_id: str) -> bool:
    return bool(_run_tests(ws).get(node_id, False))


CHECKS = {"facet_test": facet_test}
