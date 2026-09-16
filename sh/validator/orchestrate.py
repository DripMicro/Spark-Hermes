"""The round loop (spec §9.1) — every stage, unattended, forever.

    mint -> seal -> publish open -> evaluate -> close -> scorecards + crown -> export -> upload -> publish close -> next

Runs wherever the validator's credentials live; the GPU worker is reached over ssh and holds none. GitHub is
the miners' surface: a strategy is a pull request against `submissions/`, the round's tasks appear under
`rounds/<id>/tasks/` when the round opens, and everything the round produced — the revealed withheld halves and
their salts, the scores, the leaderboard, every scorecard — is committed under `rounds/<id>/` when it closes.
`docs/live/live.json` is rewritten at every stage change and every few minutes during evaluation, and the
dashboard at `docs/live/` polls it. Nothing a miner is judged by is kept where a miner cannot see it.

The round's verdict is enforced on the PRs themselves: the crowned strategy's PR is **merged** into
`submissions/` and defends the crown as an incumbent in every later round; every other competition PR the
seal named is **closed** with the reason, and a miner who wants another go opens a new one. PRs the seal never
named — maintenance, dependencies — are never touched.

Transparency rules the loop enforces, each because its absence would let a validator cheat quietly:

  * a bundle is sealed into a round by its PR head SHA and digest *before* any evaluation, and the seal is
    published with the tasks — a validator cannot pick which submission "counted" after seeing results;
  * the withheld half is committed to in the published task and revealed at close with its salt;
  * a PR that appears after the seal is told, on the PR, that it is active from the next round;
  * the crown is the top weight of the *published* close.json, recomputable by anyone.

    python -m sh.validator.orchestrate --once                       # one round
    python -m sh.validator.orchestrate --mock-miners DIR            # forever, with mock challengers resubmitting
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from sh.cli.lint import bundle_digest, collect, lint
from sh.cli.scorecard import render as render_scorecard
from sh.exports.build import build as build_exports
from sh.exports.upload import upload as upload_exports
from sh.validator.round import close as close_round
from sh.web.build import render as render_leaderboard

REPO = "gittensor-model-hub/Spark-Hermes"
BRANCH = "sh/v2-pipeline"
LABEL_STRATEGY, LABEL_SCORED, LABEL_CROWN = "sh:strategy", "sh:round:scored", "sh:round:crown"
HF_REPO = "gittensor-model-hub/spark-hermes-rounds"
LIVE = "docs/live/live.json"  # what the dashboard polls; committed on every stage change


@dataclass
class Config:
    """The control plane runs wherever the validator's credentials live; the GPU worker is reached over ssh and
    holds no credentials at all — it receives a round directory, runs episodes, and hands the episodes back."""

    state: Path  # durable validator state: rounds/, archive/, salt secret
    repo: Path  # a checkout of BRANCH the loop commits to
    supply: Path  # the private supply package's parent
    pkg: Path  # the public package's parent
    worker: str = "root@91.224.44.223"
    worker_port: int = 50199
    worker_root: str = "/root/sh"  # holds pkg/ (the public package), state/tokens, state/usage
    image: str = "family-process-lifecycle:pin"
    family: str = "process_lifecycle"
    difficulty: int = 3
    tasks_per_round: int = 8
    window: int = 8
    concurrency: int = 2
    era: str = "e0"

    @property
    def rounds(self) -> Path:
        return self.state / "rounds"


def sh(cmd: list[str], *, cwd: Path | None = None, env: dict | None = None, check: bool = True) -> str:
    r = subprocess.run(cmd, cwd=cwd, env={**os.environ, **(env or {})}, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(cmd[:4])}… exited {r.returncode}: {r.stderr[-800:]}")
    return r.stdout


def gh(*args: str) -> str:
    return sh(["gh", *args])


def _secret(cfg: Config, name: str) -> str:
    return (cfg.state / name).read_text().strip()


def _worker(cfg: Config, cmd: str) -> str:
    return sh(
        ["ssh", "-o", "BatchMode=yes", "-o", "ServerAliveInterval=30", "-p", str(cfg.worker_port), cfg.worker, cmd],
        check=False,
    )


def _worker_launch(cfg: Config, cmd: str) -> None:
    """Start a long-running command on the worker and come back at once.

    A plain `ssh host 'cmd &'` does not return until sshd sees every pipe close, and in round r0001 it held the
    control plane for the entire evaluation — the progress loop never ran and the dashboard sat on "publish".
    `-f` backgrounds ssh after authentication and `-n` detaches stdin, so this returns as soon as the remote
    shell accepts the command; the polling loop, not this call, is the source of truth for whether the job is
    running. A timeout guards the remaining case where even the handshake hangs."""
    try:
        subprocess.run(
            ["ssh", "-f", "-n", "-o", "BatchMode=yes", "-p", str(cfg.worker_port), cfg.worker, cmd],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        pass


def _rsync(src: str, dst: str, cfg: Config) -> None:
    sh(["rsync", "-az", "--delete", "-e", f"ssh -o BatchMode=yes -p {cfg.worker_port}", src, dst])


# ─── round bookkeeping ─────────────────────────────────────────────────────────────────────────────
def next_round_id(cfg: Config) -> str:
    cfg.rounds.mkdir(parents=True, exist_ok=True)
    done = sorted(p.name for p in cfg.rounds.iterdir() if p.is_dir() and p.name.startswith("r"))
    n = int(done[-1][1:]) + 1 if done else 1
    return f"r{n:04d}"


def log(rd: Path, stage: str, **fields) -> None:
    rec = {"t": time.time(), "stage": stage, **fields}
    with (rd / "phases.jsonl").open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"[{rd.name}] {stage} {json.dumps(fields)[:200]}", flush=True)


def _commit(cfg: Config, message: str, paths: tuple[str, ...] = ("rounds", "docs/live", "docs/rounds")) -> None:
    sh(["git", "add", *paths], cwd=cfg.repo)
    if sh(["git", "status", "--porcelain", *paths], cwd=cfg.repo).strip():
        sh(
            ["git", "commit", "-q", "-m", message, "--", *paths], cwd=cfg.repo
        )  # only these paths, whatever else is staged
        sh(["git", "pull", "-q", "--rebase", "origin", BRANCH], cwd=cfg.repo, check=False)
        sh(["git", "push", "-q", "origin", BRANCH], cwd=cfg.repo)


def live(cfg: Config, rd: Path, stage: str, *, progress: dict | None = None, push: bool = True) -> None:
    """The dashboard's single source: the current round's stage and progress, and the closed-round history."""
    phases_path = rd / "phases.jsonl"
    phases = [json.loads(line) for line in phases_path.read_text().splitlines()] if phases_path.exists() else []
    seal_path, index_path = rd / "seal.json", cfg.repo / "rounds" / "index.json"
    sealed = json.loads(seal_path.read_text()) if seal_path.exists() else {}
    history = json.loads(index_path.read_text())["rounds"] if index_path.exists() else []
    # Once the round has closed, its scores travel with the live state so the dashboard can show them at once,
    # in the same shape the leaderboard and scorecards use — the same numbers, never a re-derivation.
    close_path = rd / "close" / "close.json"
    closed = json.loads(close_path.read_text()) if close_path.exists() else None
    if progress is None:  # stages after evaluation carry the counts forward rather than blanking the board
        prev_path = cfg.repo / LIVE
        prev = json.loads(prev_path.read_text()) if prev_path.exists() else {}
        progress = prev.get("progress") if prev.get("round_id") == rd.name else None
    scores = None
    if closed:
        weights = closed.get("weights", {})
        scores = {
            "weights": weights,
            "king": max(weights, key=lambda h: weights[h]) if weights and max(weights.values()) > 0 else None,
            "per_hotkey": {
                h: {
                    k: s.get(k)
                    for k in ("n", "score", "mean_d", "se", "delta_c", "gate", "overfit_rate", "dq", "reason")
                }
                for h, s in closed.get("scores", {}).items()
            },
            "family_stats": {
                f: {"null_p": r["null"].get("p"), "canon_p": r["canon"].get("p"), "label": r.get("label")}
                for f, r in closed.get("family_stats", {}).items()
            },
            "commitments_ok": closed.get("commitments_ok"),
        }
    state = {
        "schema": "sh-live-v2",
        "updated": time.time(),
        "round_id": rd.name,
        "stage": stage,
        "started": phases[0]["t"] if phases else time.time(),
        "phases": [{"stage": p["stage"], "t": p["t"]} for p in phases],
        "tasks": len(list((rd / "tasks").glob("*.json"))) if (rd / "tasks").exists() else 0,
        "active": sealed.get("active", {}),
        "rejected": sealed.get("rejected", {}),
        "progress": progress or {},
        "scores": scores,
        "history": history[-20:],
        "repo": REPO,
        "branch": BRANCH,
        "hf_repo": HF_REPO,
    }
    out = cfg.repo / LIVE
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(state, indent=1))
    if push:
        _commit(cfg, f"{rd.name}: live — {stage}", paths=("docs/live",))


# ─── stages ────────────────────────────────────────────────────────────────────────────────────────
def mint(cfg: Config, round_id: str, rd: Path) -> None:
    """mint -> derive -> gate -> seal, with the validator's real salt secret."""
    sh(
        [
            sys.executable,
            "-m",
            "supply.mint",
            "--round",
            round_id,
            "--plan",
            f"{cfg.family}:{cfg.tasks_per_round}:{cfg.difficulty}",
            "--out",
            str(rd),
        ],
        cwd=cfg.supply,
        env={"PYTHONPATH": f"{cfg.pkg}:{cfg.supply}", "SH_SALT_SECRET": _secret(cfg, "salt_secret")},
    )
    fam = cfg.supply / "supply" / "families" / cfg.family
    shutil.copytree(fam / "canon", rd / "canon", dirs_exist_ok=True)
    (rd / "checks").mkdir(exist_ok=True)
    shutil.copy(fam / "checks.py", rd / "checks" / f"{cfg.family}.py")
    n = len(list((rd / "tasks").glob("*.json")))
    if not n:
        raise RuntimeError("minted no tasks")
    log(rd, "mint", tasks=n)


def _bundle_from_tree(cfg: Config, ref: str, hotkey: str, dest: Path) -> dict | None:
    """Materialise `submissions/<hotkey>/` as of `ref` into `dest`; None if there is nothing there."""
    listing = sh(["git", "ls-tree", "-r", "--name-only", ref, f"submissions/{hotkey}/"], cwd=cfg.repo, check=False)
    prefix = f"submissions/{hotkey}/"
    rels = [r for r in listing.split() if r.startswith(prefix)]
    if not rels:
        return None
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    for rel in rels:
        out = dest / rel[len(prefix) :]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(sh(["git", "show", f"{ref}:{rel}"], cwd=cfg.repo).encode())
    files, problems = collect(dest)
    problems += lint(files)
    return {"files": files, "problems": problems, "digest": bundle_digest(files)}


def _changed_submissions(cfg: Config, base: str, head: str) -> list[str]:
    names = sh(["git", "diff", "--name-only", base, head, "--", "submissions/"], cwd=cfg.repo, check=False)
    return sorted({p.split("/")[1] for p in names.split() if p.count("/") >= 2 and p.split("/")[1] != "README.md"})


def pr_role(changed: list[str]) -> str:
    """What a pull request is to the round, from the submission directories it touches: none — maintenance,
    never sealed, never closed by a round; one — a strategy; more — a strategy PR done wrong, rejected."""
    return "maintenance" if not changed else "strategy" if len(changed) == 1 else "malformed"


def _strategy_prs(cfg: Config, tip: str) -> list[dict]:
    """Every open PR against the branch that touches `submissions/`, with the directories it changes. Recognised
    by content, not by label — a miner cannot label a PR — and labelled `sh:strategy` here so the board can see
    it. Fork heads are fetched by their pull ref; `origin` alone carries only same-repository branches."""
    sh(["git", "fetch", "-q", "origin", "+refs/pull/*/head:refs/remotes/origin/pr/*"], cwd=cfg.repo, check=False)
    prs = json.loads(
        gh(
            "pr",
            "list",
            "--repo",
            REPO,
            "--base",
            BRANCH,
            "--state",
            "open",
            "--json",
            "number,headRefOid,headRefName,title,labels",
            "--limit",
            "100",
        )
    )
    out = []
    for pr in prs:
        changed = _changed_submissions(cfg, tip, pr["headRefOid"])
        if not changed:
            continue
        if LABEL_STRATEGY not in {lb["name"] for lb in pr.get("labels", [])}:
            sh(
                [
                    "gh",
                    "api",
                    "-X",
                    "POST",
                    f"repos/{REPO}/issues/{pr['number']}/labels",
                    "-f",
                    f"labels[]={LABEL_STRATEGY}",
                ],
                check=False,
            )
        out.append({**pr, "changed": changed})
    return out


def seal(cfg: Config, round_id: str, rd: Path) -> dict:
    """Which bundles are in this round, decided before any evaluation and published with the tasks.

    Two sources. **Incumbents**: strategies already merged into `submissions/` on the branch — a crowned king
    defends the crown every round without resubmitting. **Challengers**: every open PR touching `submissions/` whose lint
    passes, taken at its head SHA so a later push cannot change what was sealed, and carrying exactly one new
    or changed submission. A challenger for a hotkey supersedes that hotkey's incumbent."""
    sh(["git", "fetch", "-q", "origin"], cwd=cfg.repo)
    bundles = rd / "bundles"
    bundles.mkdir(exist_ok=True)
    tip = f"origin/{BRANCH}"
    active: dict[str, dict] = {}
    rejected: dict[str, str] = {}
    listing = sh(["git", "ls-tree", "--name-only", tip, "submissions/"], cwd=cfg.repo, check=False)
    for entry in listing.split():
        hotkey = entry.split("/")[-1]
        if not hotkey or hotkey == "README.md":
            continue
        b = _bundle_from_tree(cfg, tip, hotkey, bundles / hotkey)
        if b and not b["problems"]:
            active[hotkey] = {"pr": None, "head": tip, "bundle_sha256": b["digest"], "incumbent": True}
    for pr in _strategy_prs(cfg, tip):
        head, changed = pr["headRefOid"], pr["changed"]
        if pr_role(changed) == "malformed":
            rejected[str(pr["number"])] = f"{len(changed)} changed submission directories (need exactly 1)"
            continue
        hotkey = changed[0]
        b = _bundle_from_tree(cfg, head, hotkey, bundles / hotkey)
        if b is None or b["problems"]:
            rejected[str(pr["number"])] = (b or {}).get("problems", ["empty submission"])[0]
            shutil.rmtree(bundles / hotkey, ignore_errors=True)
            continue
        active[hotkey] = {"pr": pr["number"], "head": head, "bundle_sha256": b["digest"], "incumbent": False}
    record = {
        "schema": "sh-seal-v2",
        "round_id": round_id,
        "sealed_at": time.time(),
        "active": active,
        "rejected": rejected,
    }
    (rd / "seal.json").write_text(json.dumps(record, indent=1))
    log(
        rd,
        "seal",
        active=len(active),
        incumbents=sum(1 for a in active.values() if a["incumbent"]),
        rejected=len(rejected),
    )
    return record


def publish_open(cfg: Config, round_id: str, rd: Path) -> None:
    """The tasks (with their withheld commitments) and the seal, committed where miners can read them."""
    dest = cfg.repo / "rounds" / round_id
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(rd / "tasks", dest / "tasks", dirs_exist_ok=True)
    shutil.copy(rd / "seal.json", dest / "seal.json")
    sealed = json.loads((rd / "seal.json").read_text())
    live(cfg, rd, "evaluate", progress={"done": 0, "total": 0, "by_surface": {}}, push=False)
    _commit(
        cfg,
        f"{round_id}: open — {len(list((rd / 'tasks').glob('*.json')))} sealed instances, "
        f"{len(sealed['active'])} active bundles",
    )
    log(rd, "publish_open")


def _progress(cfg: Config, remote: str, total: int) -> dict:
    """Per-surface counts from the worker's episode records so far — what the dashboard shows mid-round."""
    raw = _worker(
        cfg,
        f"cd {remote}/episodes 2>/dev/null && for s in *; do "
        f"n=$(ls $s/*/episode.json 2>/dev/null | wc -l); "
        f"v=$(grep -l '\"verified_success\": true' $s/*/episode.json 2>/dev/null | wc -l); "
        f'echo "$s $n $v"; done',
    )
    by = {}
    for line in raw.split("\n"):
        parts = line.split()
        if len(parts) == 3 and parts[1].isdigit():
            by[parts[0]] = {"n": int(parts[1]), "verified": int(parts[2])}
    return {"done": sum(v["n"] for v in by.values()), "total": total, "by_surface": by}


def evaluate(cfg: Config, rd: Path, sealed: dict) -> None:
    """Runs on the GPU worker in the background while this side publishes progress every few minutes. The
    worker gets exactly what an episode needs — tasks, withheld halves for the grader, checks, canon, the sealed
    bundles — and hands the episodes back. No credential is ever on it."""
    remote = f"{cfg.worker_root}/rounds/{rd.name}"
    _worker(cfg, f"mkdir -p {remote}")
    for sub in ("tasks", "withheld", "checks", "canon", "bundles"):
        if (rd / sub).exists():
            _rsync(f"{rd / sub}/", f"{cfg.worker}:{remote}/{sub}/", cfg)
    surfaces = ["null", f"canon={remote}/canon"] + [f"{h}={remote}/bundles/{h}" for h in sealed["active"]]
    total = len(surfaces) * len(list((rd / "tasks").glob("*.json")))
    # Resume-safe: if the control plane restarted mid-round, the batch may still be running on the worker.
    # Launching a second one would double the load on the engine (which refuses at that point) and race the
    # first on the same episode directories. If it is not running, launching is always safe — `batch` resumes
    # on its own episode records and re-runs nothing that finished.
    already = _worker(cfg, f"pgrep -f 'batch --round {remote}' | wc -l").strip() not in ("", "0")
    if already:
        log(rd, "evaluate_resume", note="batch already running on the worker; polling")
    else:
        _worker_launch(
            cfg,
            f"cd {cfg.worker_root}/pkg && PYTHONPATH={cfg.worker_root}/pkg setsid nohup python3 -m sh.validator.batch "
            f"--round {remote} --surfaces {','.join(surfaces)} --image {cfg.image} --inference unused "
            f"--out {remote}/episodes --concurrency {cfg.concurrency} --network sh-ep "
            f"--tokens {cfg.worker_root}/state/tokens --usage-dir {cfg.worker_root}/state/usage "
            f"> {remote}/batch.log 2>&1 < /dev/null & echo started",
        )
    last_push = 0.0
    while True:
        time.sleep(45)
        running = _worker(cfg, f"pgrep -f 'batch --round {remote}' | wc -l").strip()
        prog = _progress(cfg, remote, total)
        if running == "0" or time.time() - last_push > 150:
            live(cfg, rd, "evaluate", progress=prog)
            last_push = time.time()
        if running == "0":
            break
    _rsync(f"{cfg.worker}:{remote}/episodes/", f"{rd / 'episodes'}/", cfg)
    n = len(list((rd / "episodes").rglob("episode.json")))
    if not n:
        raise RuntimeError("the worker returned no episodes")
    log(rd, "evaluate", episodes=n, surfaces=len(surfaces))


def window_archive(cfg: Config, round_id: str) -> Path:
    """The last W rounds' episodes, pooled: what the scorer sees. Each round's episodes are archived once,
    under the round they belong to, so a re-run of the loop never double-counts."""
    archive = cfg.state / "archive"
    archive.mkdir(exist_ok=True)
    src = cfg.rounds / round_id / "episodes"
    dst = archive / round_id
    if src.exists() and not dst.exists():
        shutil.copytree(src, dst)
    rounds = sorted(p.name for p in archive.iterdir() if p.is_dir())[-cfg.window :]
    pooled = cfg.state / "window"
    shutil.rmtree(pooled, ignore_errors=True)
    for r in rounds:
        shutil.copytree(archive / r, pooled / r)
    (pooled / "rounds.json").write_text(json.dumps(rounds))
    return pooled


def close(cfg: Config, round_id: str, rd: Path) -> dict:
    pooled = window_archive(cfg, round_id)
    window = json.loads((pooled / "rounds.json").read_text())
    record = close_round(rd, pooled, rd / "close", reveal_dir=rd / "withheld", era=cfg.era, window=window)
    log(
        rd,
        "close",
        window=window,
        episodes=record["episodes"],
        commitments_ok=record["commitments_ok"],
        weights=record["weights"],
    )
    return record


def outcome(sealed: dict, weights: dict) -> dict:
    """What happens to each PR the seal named: the top weight's PR is merged, every other challenger's is
    closed. Pure, so it is testable. Only PRs the seal named are ever touched — a maintenance PR is never in
    the seal, so it is never closed by the round."""
    king = max(weights, key=lambda h: weights[h]) if weights and max(weights.values()) > 0 else None
    king_pr = sealed["active"].get(king, {}).get("pr") if king else None
    close_prs = sorted(
        {info["pr"] for h, info in sealed["active"].items() if info.get("pr") and h != king}
        | {int(n) for n in sealed.get("rejected", {})}
    )
    return {"king": king, "merge": king_pr, "close": close_prs}


def announce(cfg: Config, round_id: str, rd: Path, record: dict, sealed: dict) -> str | None:
    """Scorecards on every PR; `scored` on every PR; the crown moved to the king; the king's PR merged; every
    other competition PR closed with the reason. Returns the king."""
    reveal = json.loads((rd / "close" / "reveal.json").read_text())
    (rd / "scorecards").mkdir(exist_ok=True)
    plan = outcome(sealed, record["weights"])
    king = plan["king"]
    for hotkey, info in sealed["active"].items():
        card = render_scorecard(record, hotkey, reveal)
        (rd / "scorecards" / f"{hotkey}.md").write_text(card)
        if not info.get("pr"):
            continue  # an incumbent has no PR to write to; its card is published with the round
        body = f"### Round `{round_id}`\n\n" + card
        if hotkey == king:
            body = "👑 **Crowned: top weight this round. Merging.**\n\n" + body
        else:
            body += (
                f"\n\n---\nNot crowned in `{round_id}`; this PR is closed with the round. "
                "Resubmit to compete in the next one."
            )
        gh("pr", "comment", str(info["pr"]), "--repo", REPO, "--body", body)
        gh("api", "-X", "POST", f"repos/{REPO}/issues/{info['pr']}/labels", "-f", f"labels[]={LABEL_SCORED}")
    # One crown. Remove it wherever it was; place it on the king's PR.
    crowned = json.loads(
        gh("pr", "list", "--repo", REPO, "--label", LABEL_CROWN, "--state", "all", "--json", "number", "--limit", "100")
    )
    for pr in crowned:
        sh(["gh", "api", "-X", "DELETE", f"repos/{REPO}/issues/{pr['number']}/labels/{LABEL_CROWN}"], check=False)
    if plan["merge"]:
        gh("api", "-X", "POST", f"repos/{REPO}/issues/{plan['merge']}/labels", "-f", f"labels[]={LABEL_CROWN}")
        merged = subprocess.run(
            [
                "gh",
                "pr",
                "merge",
                str(plan["merge"]),
                "--repo",
                REPO,
                "--squash",
                "--subject",
                f"crown {round_id}: {king}",
            ],
            capture_output=True,
            text=True,
        )
        log(rd, "merge", pr=plan["merge"], ok=merged.returncode == 0, err=merged.stderr[-200:])
    elif king:
        log(rd, "merge", pr=None, ok=True, note="incumbent retains the crown")
    for number in plan["close"]:
        reason = sealed.get("rejected", {}).get(str(number))
        why = f"rejected at seal: {reason}" if reason else f"not crowned in `{round_id}`"
        sh(
            [
                "gh",
                "pr",
                "close",
                str(number),
                "--repo",
                REPO,
                "--comment",
                f"Closed with round `{round_id}` — {why}. Resubmit to compete in the next round.",
            ],
            check=False,
        )
    sealed_prs = {i["pr"] for i in sealed["active"].values() if i.get("pr")} | {
        int(n) for n in sealed.get("rejected", {})
    }
    sh(["git", "fetch", "-q", "origin"], cwd=cfg.repo)
    for pr in _strategy_prs(cfg, f"origin/{BRANCH}"):
        if pr["number"] not in sealed_prs:
            gh(
                "pr",
                "comment",
                str(pr["number"]),
                "--repo",
                REPO,
                "--body",
                f"Arrived after round `{round_id}` was sealed; active from the next round.",
            )
    log(rd, "announce", king=king, merged=plan["merge"], closed=plan["close"])
    return king


def export_and_upload(cfg: Config, round_id: str, rd: Path) -> dict:
    manifest = build_exports(rd, rd / "episodes", rd / "close" / "close.json", rd / "export")
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        log(
            rd, "export", sft=manifest["sft_rows"], dpo=manifest["dpo_pairs"], uploaded=False, reason="HF_TOKEN not set"
        )
        return {"manifest": manifest, "upload": {"uploaded": False, "reason": "HF_TOKEN not set"}}
    result = upload_exports(rd / "export", HF_REPO, token, round_id=round_id)
    log(
        rd,
        "export",
        sft=manifest["sft_rows"],
        dpo=manifest["dpo_pairs"],
        uploaded=result.get("uploaded"),
        url=result.get("url"),
    )
    return {"manifest": manifest, "upload": result}


def publish_close(cfg: Config, round_id: str, rd: Path, record: dict, king: str | None, exported: dict) -> None:
    """Everything a miner needs to check the round, in the repository, under the round."""
    sh(["git", "pull", "-q", "--rebase", "origin", BRANCH], cwd=cfg.repo, check=False)  # the merge just landed
    dest = cfg.repo / "rounds" / round_id
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("close.json", "reveal.json"):
        shutil.copy(rd / "close" / name, dest / name)
    shutil.copytree(rd / "checks", dest / "checks", dirs_exist_ok=True)  # semantics of `custom` predicates
    shutil.copytree(rd / "scorecards", dest / "scorecards", dirs_exist_ok=True)
    shutil.copy(rd / "export" / "manifest.json", dest / "manifest.json")
    artefacts = sorted(p.name for p in dest.iterdir())
    entry = {
        "round_id": round_id,
        "closed_at": time.time(),
        "episodes": record["episodes"],
        "king": king,
        "weights": record["weights"],
        "commitments_ok": record["commitments_ok"],
        "sft_rows": exported["manifest"]["sft_rows"],
        "dpo_pairs": exported["manifest"]["dpo_pairs"],
        "hf": exported["upload"].get("url"),
    }
    index_path = cfg.repo / "rounds" / "index.json"
    index = (
        json.loads(index_path.read_text()) if index_path.exists() else {"schema": "sh-rounds-index-v2", "rounds": []}
    )
    index["rounds"] = [r for r in index["rounds"] if r["round_id"] != round_id] + [entry]
    index_path.write_text(json.dumps(index, indent=1))
    page = cfg.repo / "docs" / "rounds" / round_id  # the round's page, where Pages serves it
    page.mkdir(parents=True, exist_ok=True)
    (page / "index.html").write_text(
        render_leaderboard(record, {**entry, "artefacts": artefacts, "repo": REPO, "branch": BRANCH})
    )
    live(cfg, rd, "done", push=False)
    _commit(
        cfg,
        f"{round_id}: close — king {king or 'none'}, {record['episodes']} episodes, "
        f"{exported['manifest']['sft_rows']} SFT rows, {exported['manifest']['dpo_pairs']} DPO pairs",
    )
    log(rd, "publish_close", king=king)


# ─── the round, and the loop ───────────────────────────────────────────────────────────────────────
def done_stages(rd: Path) -> set[str]:
    """The stages a round has completed, from its own log — what a restart resumes from (spec §5.7)."""
    p = rd / "phases.jsonl"
    if not p.exists():
        return set()
    return {json.loads(line)["stage"] for line in p.read_text().splitlines() if line.strip()}


def unfinished_round(cfg: Config) -> Path | None:
    """The latest round directory without a DONE marker, if any — the one a restarted loop must pick up."""
    if not cfg.rounds.exists():
        return None
    rounds = sorted(p for p in cfg.rounds.iterdir() if p.is_dir() and p.name.startswith("r"))
    if rounds and not (rounds[-1] / "DONE").exists():
        return rounds[-1]
    return None


def run_round(cfg: Config, mock_miners: Path | None = None, resume: Path | None = None) -> dict:
    """One round. With `resume`, the stages that round already logged are skipped, and the seal that was
    published is reused rather than recomputed — a restart must never change what a round sealed."""
    if resume:
        rd, round_id = resume, resume.name
        done = done_stages(rd)
        log(rd, "resume", completed=sorted(done))
    else:
        round_id = next_round_id(cfg)
        rd = cfg.rounds / round_id
        rd.mkdir(parents=True)
        done = set()
        log(rd, "start")
    if "mint" not in done:
        live(cfg, rd, "mint")
        mint(cfg, round_id, rd)
    if "seal" not in done:
        sealed = seal(cfg, round_id, rd)
    else:
        sealed = json.loads((rd / "seal.json").read_text())
    if "publish_open" not in done:
        publish_open(cfg, round_id, rd)
    if "evaluate" not in done:
        evaluate(cfg, rd, sealed)
    live(cfg, rd, "close")
    record = close(cfg, round_id, rd)
    if "announce" not in done:
        king = announce(cfg, round_id, rd, record, sealed)
    else:  # announced before the restart: the king is in the round's own log
        king = next(
            (
                json.loads(line).get("king")
                for line in (rd / "phases.jsonl").read_text().splitlines()
                if json.loads(line).get("stage") == "announce"
            ),
            None,
        )
    live(cfg, rd, "export", push=False)
    exported = export_and_upload(cfg, round_id, rd)
    publish_close(cfg, round_id, rd, record, king, exported)
    (rd / "DONE").write_text(json.dumps({"king": king, "weights": record["weights"]}))
    log(rd, "done", king=king)
    if mock_miners:
        from sh.cli.mock_miners import open_prs

        opened = open_prs(mock_miners, REPO, BRANCH, cfg.repo, skip={king} if king else set())
        log(rd, "mock_resubmit", opened=opened)
    return {"round_id": round_id, "king": king, "weights": record["weights"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=os.environ.get("SH_STATE", str(Path.home() / ".spark-hermes-state")))
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--supply", default=str(Path(__file__).resolve().parents[3] / "Spark-Hermes-Withheld"))
    ap.add_argument("--pkg", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--tasks", type=int, default=8)
    ap.add_argument("--difficulty", type=int, default=3)
    ap.add_argument("--window", type=int, default=8)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--pause", type=int, default=60, help="seconds between rounds")
    ap.add_argument("--mock-miners", help="directory of mock miner bundles to resubmit after each round (test only)")
    a = ap.parse_args(argv)
    cfg = Config(
        state=Path(a.state),
        repo=Path(a.repo),
        supply=Path(a.supply),
        pkg=Path(a.pkg),
        tasks_per_round=a.tasks,
        difficulty=a.difficulty,
        window=a.window,
    )
    resume = unfinished_round(cfg)  # a restart picks up the round it was in the middle of
    while True:
        try:
            result = run_round(cfg, Path(a.mock_miners) if a.mock_miners else None, resume=resume)
            resume = None
            print(json.dumps(result), flush=True)
        except Exception as e:  # a failed round is logged and the loop goes on
            print(f"round failed: {e!r}", flush=True)
            if a.once:
                return 1
        if a.once:
            return 0
        time.sleep(a.pause)


if __name__ == "__main__":
    sys.exit(main())
