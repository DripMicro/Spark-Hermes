"""Mock miners for end-to-end testing: resubmit a set of strategies as fresh pull requests.

The real competition closes every strategy PR that was not crowned, so a miner who wants to compete next round
opens a new one. This helper plays that miner, for several hotkeys at once, so the loop always has challengers.
It is a test fixture and lives in `sh/cli` only because the CLI is where the lint it reuses lives.

It works in its own temporary git worktree, never in the checkout it is handed: the orchestrator commits from
that checkout, and a branch switch under it would send the round's artefacts to the wrong branch.

    python -m sh.cli.mock_miners --miners DIR --repo OWNER/REPO --base BRANCH --checkout PATH
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from sh.cli.lint import check

LABEL = "sh:strategy"
_SUFFIX = re.compile(r"-\d{9,}$")  # the timestamp a resubmission branch carries


def _run(cmd: list[str], cwd: Path | None = None, check_rc: bool = True) -> str:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check_rc and r.returncode:
        raise RuntimeError(f"{' '.join(cmd[:3])}… exited {r.returncode}: {r.stderr[-400:]}")
    return r.stdout


def _open_hotkeys(repo: str, base: str) -> dict[str, int]:
    """Hotkeys that already have an open strategy PR, from the branch name `miner/<hotkey>[-<ts>]`."""
    out = {}
    prs = json.loads(
        _run(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--base",
                base,
                "--label",
                LABEL,
                "--state",
                "open",
                "--json",
                "number,headRefName",
                "--limit",
                "100",
            ]
        )
    )
    for pr in prs:
        name = pr["headRefName"].split("/")[-1]
        out[_SUFFIX.sub("", name)] = pr["number"]
    return out


def open_prs(miners: Path, repo: str, base: str, checkout: Path, *, skip: set[str] = frozenset()) -> dict:
    """One PR per miner directory that does not already have an open one. Returns {hotkey: pr_number}."""
    existing = _open_hotkeys(repo, base)
    _run(["git", "fetch", "-q", "origin", base], cwd=checkout)
    tmp = Path(tempfile.mkdtemp(prefix="sh-mock-miners-"))
    wt = tmp / "wt"
    opened = {}
    try:
        _run(["git", "worktree", "add", "-q", "--detach", str(wt), f"origin/{base}"], cwd=checkout)
        for bundle in sorted(p for p in miners.iterdir() if p.is_dir()):
            hotkey = bundle.name
            if hotkey in skip or hotkey in existing:
                continue
            verdict = check(bundle)
            if not verdict["ok"]:
                print(f"{hotkey}: lint failed, not submitting: {verdict['problems'][0]}", file=sys.stderr)
                continue
            branch = f"miner/{hotkey}-{int(time.time())}"
            _run(["git", "checkout", "-q", "-B", branch, f"origin/{base}"], cwd=wt)
            dest = wt / "submissions" / hotkey
            shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(bundle, dest)
            _run(["git", "add", f"submissions/{hotkey}"], cwd=wt)
            _run(["git", "commit", "-q", "-m", f"miner: {hotkey}\n\nbundle_sha256 {verdict['bundle_sha256']}"], cwd=wt)
            _run(["git", "push", "-q", "-u", "origin", branch], cwd=wt)
            url = _run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--repo",
                    repo,
                    "--base",
                    base,
                    "--head",
                    branch,
                    "--title",
                    f"miner: {hotkey}",
                    "--body",
                    f"Strategy submission for hotkey `{hotkey}`.\n\n`bundle_sha256` "
                    f"`{verdict['bundle_sha256']}`. Linted with `python -m sh.cli.lint` — ok.",
                ]
            ).strip()
            number = int(url.rstrip("/").split("/")[-1])
            _run(["gh", "api", "-X", "POST", f"repos/{repo}/issues/{number}/labels", "-f", f"labels[]={LABEL}"])
            opened[hotkey] = number
            time.sleep(1.1)  # distinct branch timestamps
    finally:
        _run(["git", "worktree", "remove", "--force", str(wt)], cwd=checkout, check_rc=False)
        shutil.rmtree(tmp, ignore_errors=True)
    return opened


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--miners", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--checkout", required=True)
    a = ap.parse_args(argv)
    print(json.dumps(open_prs(Path(a.miners), a.repo, a.base, Path(a.checkout)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
