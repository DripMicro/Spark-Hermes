"""The miner's CLI: fetch the current round's tasks, submit a signed strategy, see where you stand.

    python -m sh.cli.miner tasks  [--out tasks/]                       # this round's tasks (swe_fix: practice bugs)
    python -m sh.cli.miner submit --bundle DIR --key HOTKEY_FILE       # one PR per hotkey per round; resubmit to replace
    python -m sh.cli.miner status [--hotkey SS58]

Only the open round's tasks are in the repository — future rounds exist as digests until they open — so `tasks`
cannot fetch ahead. For a family that evaluates on hidden bugs (swe_fix) they are the round's previews: sibling bugs
from the repositories the round is scored on. `submit` lints the bundle and signs
`spark-hermes:<repo>:<round_id>:<bundle_sha256>:<signed_at>` with the hotkey, then pushes `miner/<hotkey>` from a
temporary worktree: the first push opens the pull request, every later push replaces it. With a submission `server`
(the board advertises one, or pass `--server`) the prose is uploaded there privately and the PR carries only the
signed commitment (`attestation.json`), so a rival in the same window cannot read your strategy; without one, the
bundle itself is committed to the PR. It refuses outside the submission window, because the validator would.

A miner working from a fork passes `--head-owner <github user>`; the branch is pushed to `origin` (the fork)
and the pull request is opened against the competition repository.
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from sh.cli import attest
from sh.cli.lint import bundle_digest, check, collect

REPO = "gittensor-model-hub/Spark-Hermes"
BRANCH = "main"
RAW = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"
CONTENTS = "https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"


def _get(url: str) -> bytes:
    with urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "spark-hermes-miner"}), timeout=30
    ) as r:
        return r.read()


def current(repo: str = REPO, branch: str = BRANCH) -> dict:
    """The board's live state: round, stage, window."""
    return json.loads(_get(RAW.format(repo=repo, branch=branch, path="docs/live/live.json") + f"?t={int(time.time())}"))


def _remaining(live: dict) -> str:
    w = live.get("window") or {}
    if not w or live.get("stage") != "window":
        return "closed"
    s = max(0, int(w["closes_at"] - time.time()))
    return f"{s // 3600} h {s % 3600 // 60} min left"


def tasks(out: Path, repo: str = REPO, branch: str = BRANCH) -> dict:
    """Download the open round's tasks to `out/<round_id>/`. Refuses to guess at any other round."""
    live = current(repo, branch)
    rid, stage = live["round_id"], live["stage"]
    listing = json.loads(_get(CONTENTS.format(repo=repo, branch=branch, path=f"rounds/{rid}/tasks")))
    dest = out / rid
    dest.mkdir(parents=True, exist_ok=True)
    names = []
    for entry in listing:
        if entry.get("type") == "file" and entry["name"].endswith(".json"):
            (dest / entry["name"]).write_bytes(_get(entry["download_url"]))
            names.append(entry["name"])
    if live.get("window"):
        (dest / "window.json").write_text(json.dumps(live["window"]))
    return {"round_id": rid, "stage": stage, "window": _remaining(live), "tasks": sorted(names), "dir": str(dest)}


def _run(cmd: list[str], cwd: Path | None = None, check_rc: bool = True) -> str:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check_rc and r.returncode:
        raise RuntimeError(f"{' '.join(cmd[:3])}… exited {r.returncode}: {r.stderr[-400:]}")
    return r.stdout


def _open_pr_for(repo: str, base: str, branch: str, owner: str | None = None) -> int | None:
    """The open PR whose head is `branch` (and, for a fork, whose head repository belongs to `owner`). `gh pr list
    --head owner:branch` returns nothing, so the branch is matched and the owner filtered here."""
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
                "--head",
                branch,
                "--state",
                "open",
                "--json",
                "number,headRepositoryOwner",
            ]  # fmt: skip
        )
    )
    for pr in prs:
        if owner is None or (pr.get("headRepositoryOwner") or {}).get("login") == owner:
            return pr["number"]
    return None


def _upload(server: str, attestation: dict, files: dict) -> dict:
    """Send the prose bundle to the private submission server, which lints it, refuses answer-copies,
    and stores it under the digest the attestation committed to. Returns its JSON (ok + receipt, or
    problems). The PR never carries the prose — only the commitment this upload is bound to."""
    body = json.dumps(
        {"attestation": attestation, "files": {p: base64.b64encode(b).decode() for p, b in files.items()}}
    ).encode()
    req = urllib.request.Request(
        server.rstrip("/") + "/submit",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "spark-hermes-miner"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:  # the server answers a rejection with a JSON body of problems
        try:
            return json.load(e)
        except (ValueError, UnicodeDecodeError):
            return {"ok": False, "problems": [f"the submission server returned HTTP {e.code}"]}
    except urllib.error.URLError as e:
        return {"ok": False, "problems": [f"cannot reach the submission server: {e.reason}"]}


def _committed_digest(dest: Path, private: bool) -> str | None:
    """The digest already on the PR branch for this hotkey — to skip a byte-identical resubmission. In
    private mode the prose is not in the tree, so it is the attestation's `bundle_sha256`; in legacy
    mode it is the digest of the committed prose."""
    if not dest.is_dir():
        return None
    if private:
        try:
            return json.loads((dest / attest.FILE).read_text()).get("bundle_sha256")
        except (OSError, ValueError):
            return None
    inc_files, _ = collect(dest)
    inc_files.pop(attest.FILE, None)
    return bundle_digest(inc_files)


def submit_bundle(
    bundle: Path,
    keypair,
    *,
    round_id: str,
    repo: str = REPO,
    base: str = BRANCH,
    checkout: Path | None = None,
    head_owner: str | None = None,
    remote: str = "origin",
    server: str | None = None,
) -> dict:
    """Lint, sign for `round_id`, and open/replace the PR for `miner/<hotkey>`. With a submission
    `server` the prose is uploaded there privately and the PR carries only the signed commitment
    (`attestation.json`); without one, the bundle itself is committed to the PR (legacy)."""
    files, problems = collect(bundle)
    files.pop(attest.FILE, None)  # an old attestation is replaced, never linted
    verdict = check(bundle)
    prose_problems = [p for p in verdict["problems"] if not p.startswith("L10")]
    if prose_problems:
        return {"ok": False, "problems": prose_problems}
    digest = bundle_digest(files)
    hotkey = keypair.ss58_address
    att = attest.sign(keypair, round_id, digest)
    private = server is not None
    receipt = None
    if private:  # reveal the prose to the private server; the PR will carry only the commitment
        up = _upload(server, att, files)
        if not up.get("ok"):
            return {"ok": False, "problems": up.get("problems") or ["the submission server rejected the upload"]}
        receipt = up.get("receipt")
    checkout = checkout or Path.cwd()
    branch = f"miner/{hotkey}"
    head = f"{head_owner}:{branch}" if head_owner else branch
    _run(["git", "fetch", "-q", remote, base], cwd=checkout)
    tmp = Path(tempfile.mkdtemp(prefix="sh-submit-"))
    wt = tmp / "wt"
    try:
        _run(["git", "worktree", "add", "-q", "--detach", str(wt), f"{remote}/{base}"], cwd=checkout)
        dest = wt / "submissions" / hotkey
        if _committed_digest(dest, private) == digest:
            return {"ok": True, "hotkey": hotkey, "bundle_sha256": digest, "skipped": "already submitted, byte for byte"}
        _run(["git", "checkout", "-q", "-B", branch, f"{remote}/{base}"], cwd=wt)
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True, exist_ok=True)
        if not private:
            for rel, data in files.items():
                p = dest / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
        (dest / attest.FILE).write_text(json.dumps(att, indent=1) + "\n")
        if private and receipt is not None:
            (dest / "receipt.json").write_text(json.dumps(receipt, indent=1) + "\n")
        if private:  # the prose is not here to lint; check the commitment binds this hotkey, round and digest
            binding = attest.problems(json.loads((dest / attest.FILE).read_text()), digest=digest, hotkey=hotkey, round_id=round_id)
            if binding:
                return {"ok": False, "problems": binding}
        else:
            final = check(dest, hotkey=hotkey, round_id=round_id, require_attestation=True)
            if not final["ok"]:
                return {"ok": False, "problems": final["problems"]}
        _run(["git", "add", f"submissions/{hotkey}"], cwd=wt)
        _run(["git", "commit", "-q", "-m", f"miner: {hotkey} for {round_id}\n\nbundle_sha256 {digest}"], cwd=wt)
        _run(["git", "push", "-q", "-f", "-u", remote, branch], cwd=wt)
        number = _open_pr_for(repo, base, branch, head_owner)
        created = number is None
        if created:
            reveal = (
                "uploaded to the submission server and signed (`attestation.json`); the prose is revealed after "
                "the round is scored."
                if private
                else "signed (`attestation.json`). Linted with `python -m sh.cli.lint` — ok."
            )
            create = _run(
                [
                    "gh", "pr", "create", "--repo", repo, "--base", base, "--head", head, "--title", f"miner: {hotkey}",
                    "--body", f"Strategy for round `{round_id}` by hotkey `{hotkey}`.\n\n`bundle_sha256` `{digest}`, {reveal}",
                ],  # fmt: skip
                check_rc=False,
            ).strip()
            if create.startswith("http"):
                number = int(create.rstrip("/").split("/")[-1])
            else:  # the push updated a PR that already existed: find it rather than fail
                number = _open_pr_for(repo, base, branch, head_owner)
                created = False
                if number is None:
                    return {"ok": False, "problems": [f"pushed {branch} but could not open or find its PR"]}
        return {"ok": True, "hotkey": hotkey, "pr": number, "bundle_sha256": digest, "created": created, "private": private}
    finally:
        _run(["git", "worktree", "remove", "--force", str(wt)], cwd=checkout, check_rc=False)
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Spark-Hermes miner")
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--base", default=BRANCH)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tasks", help="fetch the open round's tasks")
    t.add_argument("--out", default="tasks")
    s = sub.add_parser("submit", help="sign and submit a strategy for the open round")
    s.add_argument("--bundle", required=True)
    s.add_argument("--key", required=True, help="bittensor hotkey file, mnemonic, or //dev URI")
    s.add_argument("--checkout", default=".", help="a clone whose `origin` you can push to")
    s.add_argument("--head-owner", help="your GitHub user, when pushing to a fork")
    s.add_argument("--round", help="override the round (normally read from the board)")
    s.add_argument("--server", help="private submission server URL (default: the board's advertised one, if any)")
    s.add_argument("--force", action="store_true", help="submit even if the window is not open")
    st = sub.add_parser("status", help="the round, the window, and your PR")
    st.add_argument("--hotkey")
    a = ap.parse_args(argv)

    if a.cmd == "tasks":
        r = tasks(Path(a.out), a.repo, a.base)
        print(f"round    {r['round_id']} ({r['stage']}; window {r['window']})")
        print(f"tasks    {len(r['tasks'])} -> {r['dir']}")
        return 0
    if a.cmd == "submit":
        live = current(a.repo, a.base)
        if live.get("stage") != "window" and not a.round and not a.force:
            print(
                f"the submission window is not open (round {live.get('round_id')} is at {live.get('stage')})",
                file=sys.stderr,
            )
            return 1
        rid = a.round or live["round_id"]
        kp = attest.load_keypair(a.key)
        r = submit_bundle(
            Path(a.bundle),
            kp,
            round_id=rid,
            repo=a.repo,
            base=a.base,
            checkout=Path(a.checkout),
            head_owner=a.head_owner,
            server=a.server or (live.get("submit_server") if isinstance(live, dict) else None),
        )
        if not r["ok"]:
            print("not submitted:", file=sys.stderr)
            for p in r["problems"]:
                print(f"  - {p}", file=sys.stderr)
            return 1
        if r.get("skipped"):
            print(f"{r['hotkey']}: {r['skipped']}")
            return 0
        mode = "prose private, PR carries the commitment" if r.get("private") else "prose in the PR"
        print(
            f"{'opened' if r['created'] else 'updated'} PR #{r['pr']} for {r['hotkey']} in {rid} "
            f"(digest {r['bundle_sha256'][:12]}…, {mode})"
        )
        return 0
    live = current(a.repo, a.base)
    print(f"round    {live['round_id']} · {live['stage']} · window {_remaining(live)}")
    if a.hotkey:
        n = _open_pr_for(a.repo, a.base, f"miner/{a.hotkey}")
        print(f"your PR  {'#' + str(n) if n else 'none open'}")
        st = (live.get("crown") or {}).get("standings", {}).get(a.hotkey)
        if st:
            delta = st.get("delta")
            print(
                f"crown    rank {st.get('rank', '—')} · Δ {'—' if delta is None else f'{delta:+.3f}'} on {st['n']} paired"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
