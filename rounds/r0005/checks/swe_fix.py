"""`custom swe_test <node id>` — one predicate per test the bug breaks. Runs inside the grading container over the
agent's final tree. Everything it needs arrives in `/ep/withheld.json` under `assets`, never in the agent's boundary:
`swe/spec.json` (the broken tests, the passing tests a fix must keep, the tracked test-infrastructure files) and
`swe/files/<path>` (the files holding the broken tests, as they were before SWE-smith deleted those tests).

The tests run in the same process as the code under repair, so that code could, in principle, rewrite their
outcomes. Four things stand against it:

  * **the tamper scan** — the agent's tree is compared with the pristine copy the task image carries at
    `/opt/sh-pristine`; a line added to any non-test file that reaches for pytest's internals or Python's import
    machinery disqualifies the episode (`tamper` in the detail; the grader turns it into `harness_tamper`);
  * **the tree is made honest** — bytecode deleted, test-infrastructure files the task did not ship removed (a
    new conftest.py, sitecustomize.py, .pth, pytest.ini), the broken tests' files written back; a *shipped* test
    file the agent modified is a protected path, which the grader disqualifies on its own;
  * **sentinels** — two tests written at grade time under names and bodies chosen then, into the directory the
    broken tests live in: one must PASS and one must FAIL, or the run is not trusted at all;
  * **outcomes come from a witness plugin**, not from parsing stdout, so a line printed from library code cannot
    stand in for a result, and a repository's own `addopts` cannot change the format.

A broken test counts only if it PASSES **and every kept test PASSES**: a fix that breaks what worked is not a fix,
and an outcome other than PASSED (an XFAIL raised from library code, a skip) is not a pass.
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
PRISTINE = "/opt/sh-pristine"
# Added to a non-test Python module, these reach for the test runner or the import machinery, which no bug fix needs.
# Code, not prose: `pytest.` must be followed by a name (`pytest.org` in a cache README is not an attribute access).
TAMPER = re.compile(
    r"\b_pytest\b|\bimport\s+pytest\b|\bfrom\s+pytest\b|\bpytest\s*\.\s*[A-Za-z_]\w*\s*[(=.\[]|sys\s*\.\s*meta_path"
    r"|sys\s*\.\s*path_hooks"
    r"|sys\s*\.\s*set(trace|profile)|threading\s*\.\s*set(trace|profile)|builtins\s*\.\s*__import__|__builtins__"
    r"|\b__import__\s*\(|importlib\s*\.\s*(import_module|reload)\s*\(|\batexit\b|sitecustomize|usercustomize"
    r"|sys\s*\.\s*modules\s*\["
)
PYTEST = (
    "source /opt/miniconda3/bin/activate >/dev/null 2>&1; conda activate testbed >/dev/null 2>&1; "
    'exec pytest --disable-warnings --color=no --tb=no -p no:cacheprovider -p no:xdist -p no:randomly -p sh_witness "$@"'
)
WITNESS = '''"""The validator's witness: every test's outcome, by node id, written where the runner reads it."""
import json, os
_seen = {}


def pytest_runtest_logreport(report):
    o = report.outcome  # passed | failed | skipped
    if report.when == "call":
        if hasattr(report, "wasxfail"):
            o = "xfail" if o == "skipped" else "xpass"
        _seen[report.nodeid] = o.upper()
    elif report.when == "setup" and o != "passed":
        _seen[report.nodeid] = "ERROR" if o == "failed" else "SKIPPED"
    elif report.when == "teardown" and o == "failed":
        _seen[report.nodeid] = "ERROR"


def pytest_sessionfinish(session, exitstatus):
    with open(os.environ["SH_WITNESS_OUT"], "w") as f:
        json.dump(_seen, f)
'''
STATUS = re.compile(r"^(\S+)\s+(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b")  # what SWE-smith's parser reads
_RESULTS: dict = {}


def parse_verbose(output: str) -> dict:
    """{node id: status} from `pytest --verbose` — kept for the index's id check; grading uses the witness."""
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
    """{broken test: counts} — PASSED, and every kept test PASSED, in a run the sentinels vouch for. Pure."""
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


def sentinel_prefix(ids) -> str:
    """The prefix this repository's test functions carry (`test_`, or `it_` where `python_functions` says so): a
    sentinel pytest does not collect is `not found`, and pytest then runs nothing at all. Pure."""
    for t in ids:
        name = t.split("[", 1)[0].split("::")[-1] if "::" in t else ""
        if "_" in name.strip("_"):
            return name.split("_")[0] + "_"
    return "test_"


def sentinel_dir(spec: dict, ws: str) -> str:
    """Beside the broken tests when they live in a Python test module; a data tree collected by a custom collector
    (pygments' example files) would swallow a new .py file, so then the nearest plain tests directory, or the root."""
    for t in spec["f2p"]:
        f = t.split("::")[0]
        if f.endswith(".py"):
            return os.path.dirname(f)
    for cand in ("tests", "test"):
        if os.path.isdir(os.path.join(ws, cand)):
            return cand
    return ""


def tamper_scan(ws: str, pristine: str) -> list:
    """Lines added to non-test Python modules, compared with the pristine tree, that reach for the test runner or
    the import machinery. [(file, line)]; [] when clean. Pure over the two trees.

    Only `.py` files outside dot-directories are read: running the tests leaves `.pytest_cache/`, `*.egg-info/` and
    the like, which say "pytest" in prose and execute nothing. Comment lines are skipped for the same reason."""
    hits = []
    for root, dirs, files in os.walk(ws):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__" and not d.endswith(".egg-info")]
        for name in files:
            path = os.path.join(root, name)
            rel = os.path.relpath(path, ws)
            if TEST_INFRA.search(rel) or not name.endswith(".py"):
                continue
            try:
                with open(path, "rb") as f:
                    now = f.read()
            except OSError:
                continue
            twin = os.path.join(pristine, rel)
            try:
                with open(twin, "rb") as f:
                    was = f.read()
            except OSError:
                was = b""
            if now == was:
                continue
            added = set(now.decode(errors="replace").splitlines()) - set(was.decode(errors="replace").splitlines())
            for line in sorted(added):
                if not line.lstrip().startswith("#") and TAMPER.search(line):
                    hits.append((rel, line.strip()[:160]))
    return hits


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
    """Scan, make the tree honest, write the broken tests back, run the suite once through the witness.
    Returns ({node id: status}, info) with info = removed, modified (shipped test files the suite itself changed),
    tamper (see `tamper_scan`; None when the image carries no pristine copy), valid (the sentinels ran true)."""
    tamper = tamper_scan(ws, PRISTINE) if os.path.isdir(PRISTINE) else None
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
        os.makedirs(os.path.dirname(path) or ws, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    # the sentinels: names and numbers chosen now, nothing in them that a scan of the tree could pick out
    prefix = sentinel_prefix([*spec["f2p"], *spec["p2p"]])
    a, b = f"{prefix}{secrets.token_hex(5)}", f"{prefix}{secrets.token_hex(5)}"
    x, y = secrets.randbelow(900) + 100, secrets.randbelow(900) + 100
    where = sentinel_dir(spec, ws)
    sentinel = os.path.join(where, f"test_{secrets.token_hex(4)}.py")
    with open(os.path.join(ws, sentinel), "w") as f:
        f.write(f"def {a}():\n    assert {x} + {y} == {x + y}\n\n\ndef {b}():\n    assert {x} * {y} == {x * y + 1}\n")
    guarded = [rel for rel in spec["infra"] if rel not in files]
    before = _digests(ws, guarded)
    work = tempfile.mkdtemp(prefix="sh-swe-")
    with open(os.path.join(work, "sh_witness.py"), "w") as f:
        f.write(WITNESS)
    witness_out = os.path.join(work, "outcomes.json")
    env = {
        **os.environ,
        "HOME": work,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": work + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else ""),
        "SH_WITNESS_OUT": witness_out,
    }
    ids = [*spec["f2p"], *spec["p2p"], f"{sentinel}::{a}", f"{sentinel}::{b}"]
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
    try:
        with open(witness_out) as f:
            statuses = json.load(f)
    except (OSError, ValueError):
        statuses = {}  # no witness: nothing ran, or something kept it from speaking — not a result either way
    os.remove(os.path.join(ws, sentinel))
    after = _digests(ws, guarded)
    info = {
        "removed": removed,
        "modified": sorted(rel for rel in guarded if before[rel] != after[rel]),
        "tamper": tamper,
        "valid": statuses.get(f"{sentinel}::{a}") == "PASSED" and statuses.get(f"{sentinel}::{b}") == "FAILED",
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
    results = verdicts(spec, statuses, info["valid"] and not info["tamper"])
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
                        "tamper": info["tamper"],
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
