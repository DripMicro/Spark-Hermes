"""`custom swe_test <node id>` — one predicate per test the bug breaks. Runs inside the grading container over the
agent's final tree. Everything it needs arrives in `/ep/withheld.json` under `assets`, never in the agent's boundary:
`swe/spec.json` (the broken tests, the passing tests a fix must keep, the tracked test-infrastructure files) and
`swe/files/<path>` (the files holding the broken tests, as they were before SWE-smith deleted those tests).

Before the suite runs, the tree is made honest: bytecode is deleted (a stale .pyc can stand in for source), and any
test-infrastructure file the task did not ship — a new conftest.py, sitecustomize.py, .pth, pytest.ini, a file
under tests/ — is removed. A modified shipped one is a protected path, so the grader disqualifies it. Then the
broken tests' files are written back and pytest runs once, on the broken tests and the kept tests together.

A broken test counts only if it PASSES **and every kept test PASSES**: a fix that breaks what worked is not a fix,
and an outcome other than PASSED (an XFAIL raised from library code, a skip) is not a pass. Two sentinel tests
named at grade time — one that must pass, one that must fail — ride along; a run that gets either wrong is not
trusted at all.
"""

import base64
import hashlib
import json
import os
import re
import secrets
import shutil
import signal
import subprocess
import tempfile

TEST_INFRA = re.compile(
    r"(^|/)(tests?|testing)/|^tests?\.py$|^test_[^/]*\.py$|^[^/]*_tests?\.py$|(^|/)conftest\.py$|(^|/)(site|user)customize\.py$"
    r"|\.pth$|^(pytest\.ini|\.pytest\.ini|tox\.ini|setup\.cfg|pyproject\.toml|setup\.py|\.coveragerc|noxfile\.py)$"
)
# SWE-smith's own parser: the node id is whatever precedes the status. Some ids end in `::` (pygments' example
# files are collected as `tests/examplefiles/<f>::`), so the id is not required to have a name after it.
STATUS = re.compile(r"^(\S+)\s+(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b")
PYTEST = (
    "source /opt/miniconda3/bin/activate >/dev/null 2>&1; conda activate testbed >/dev/null 2>&1; "
    'exec pytest --disable-warnings --color=no --tb=no --verbose -p no:cacheprovider "$@"'
)
_RESULTS: dict = {}


def parse_verbose(output: str) -> dict:
    """{node id: status} from `pytest --verbose` — the parser SWE-smith's own harness uses."""
    return {m.group(1): m.group(2) for line in output.splitlines() if (m := STATUS.match(line))}


def stray_files(ws: str, shipped: set) -> list:
    """Test-infrastructure files in the tree that the task did not ship (relative paths)."""
    out = []
    for root, dirs, files in os.walk(ws):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), ws)
            if TEST_INFRA.search(rel) and rel not in shipped:
                out.append(rel)
    return sorted(out)


def verdicts(spec: dict, statuses: dict, valid: bool = True) -> dict:
    """{broken test: counts} — PASSED, and every kept test PASSED, in a run the sentinels vouch for. Only PASSED:
    an XFAIL or SKIPPED can be raised from library code (`pytest.xfail()` in the function under repair) without
    fixing anything. Pure."""
    if not valid:
        return {t: False for t in spec["f2p"]}
    kept = all(statuses.get(t) == "PASSED" for t in spec.get("p2p", []))
    return {t: statuses.get(t) == "PASSED" and kept for t in spec["f2p"]}


def _assets() -> dict:
    ep = os.environ.get("SH_EP", "/ep")
    try:
        with open(os.path.join(ep, "withheld.json")) as f:
            return json.load(f).get("assets", {})
    except (OSError, ValueError):
        return {}


SENTINEL = """def test_{a}():
    assert 1 + 1 == 2


def test_{b}():
    assert 1 + 1 == 3
"""


def _digests(ws: str, rels) -> dict:
    out = {}
    for rel in rels:
        p = os.path.join(ws, rel)
        try:
            with open(p, "rb") as f:
                out[rel] = hashlib.sha256(f.read()).hexdigest()
        except OSError:
            out[rel] = None
    return out


def run_suite(ws: str, spec: dict, files: dict) -> tuple:
    """Make the tree honest, write the broken tests back, run the suite once. Returns ({node id: status}, info).

    Two sentinel tests ride in the same directory as the broken tests, under names chosen here and now: one must
    PASS and one must FAIL. A run in which either comes out otherwise is not a run of the tests — something in the
    tree is rewriting outcomes — and `info["valid"]` is False. `info["modified"]` lists shipped test files whose
    content the suite itself changed; a task whose suite does that is rejected at mint, since the grader would
    disqualify every agent that ran the tests.
    """
    removed = []
    for root, dirs, _ in os.walk(ws):
        for d in list(dirs):
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                dirs.remove(d)
    for rel in stray_files(ws, set(spec["infra"])):
        os.remove(os.path.join(ws, rel))
        removed.append(rel)
    for rel, data in files.items():
        path = os.path.join(ws, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    nonce = secrets.token_hex(6)
    a, b = f"sh_{nonce}_a", f"sh_{nonce}_b"
    where = os.path.dirname(spec["f2p"][0].split("::")[0])
    sentinel = os.path.join(where, f"test_sh_{nonce}.py") if where else f"test_sh_{nonce}.py"
    with open(os.path.join(ws, sentinel), "w") as f:
        f.write(SENTINEL.format(a=a, b=b))
    guarded = [rel for rel in spec["infra"] if rel not in files]
    before = _digests(ws, guarded)
    env = {**os.environ, "HOME": tempfile.mkdtemp(prefix="sh-swe-"), "PYTHONDONTWRITEBYTECODE": "1"}
    ids = [*spec["f2p"], *spec["p2p"], f"{sentinel}::test_{a}", f"{sentinel}::test_{b}"]
    with tempfile.TemporaryFile() as out:
        proc = subprocess.Popen(
            ["bash", "-c", PYTEST, "pytest", *ids],
            cwd=ws,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            proc.wait(timeout=int(spec.get("timeout_s", 900)))
        except subprocess.TimeoutExpired:
            pass
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        out.seek(0)
        statuses = parse_verbose(out.read().decode(errors="replace"))
    os.remove(os.path.join(ws, sentinel))
    after = _digests(ws, guarded)
    info = {
        "removed": removed,
        "modified": sorted(rel for rel in guarded if before[rel] != after[rel]),
        "valid": statuses.get(f"{sentinel}::test_{a}") == "PASSED"
        and statuses.get(f"{sentinel}::test_{b}") == "FAILED",
    }
    return statuses, info


def _run_tests(ws) -> dict:
    key = str(ws)
    if key in _RESULTS:
        return _RESULTS[key]
    assets = _assets()
    spec = json.loads(base64.b64decode(assets["swe/spec.json"]))
    files = {n[len("swe/files/") :]: base64.b64decode(b) for n, b in assets.items() if n.startswith("swe/files/")}
    statuses, info = run_suite(str(ws), spec, files)
    results = verdicts(spec, statuses, info["valid"])
    _RESULTS[key] = results
    try:  # every broken test's outcome beside the grade (a fraction needs all of them), and why
        outdir = os.path.join(os.environ.get("SH_EP", "/ep"), "out")
        if os.path.isdir(outdir):
            with open(os.path.join(outdir, "tests.json"), "w") as f:
                json.dump(results, f)
            with open(os.path.join(outdir, "detail.json"), "w") as f:  # the grader keeps it beside the episode
                json.dump(
                    {
                        "broken": {t: statuses.get(t, "not run") for t in spec["f2p"]},
                        "kept_failed": [t for t in spec.get("p2p", []) if statuses.get(t) != "PASSED"],
                        "kept_total": len(spec.get("p2p", [])),
                        "removed_infra": info["removed"],
                        "suite_modified": info["modified"],
                        "valid": info["valid"],
                    },
                    f,
                )
    except OSError:
        pass
    return results


def swe_test(ws, node_id: str) -> bool:
    return bool(_run_tests(ws).get(node_id, False))


CHECKS = {"swe_test": swe_test}
