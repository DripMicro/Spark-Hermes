"""The round loop (spec §9.1) — every stage, unattended, forever.

    mint -> publish -> seal -> evaluate -> close -> scorecards + crown -> export -> upload -> publish close -> next

Runs wherever the validator's credentials live; the GPU worker is reached over ssh and holds none. GitHub is
the miners' surface: a strategy is a pull request against `submissions/`,
the round's tasks appear under `rounds/<id>/tasks/` when the round opens, and everything the round produced —
the revealed withheld halves and their salts, the scores, the leaderboard, every scorecard — is committed under
`rounds/<id>/` when it closes. Nothing a miner is judged by is kept where a miner cannot see it afterwards.

Transparency rules the loop enforces, each because its absence would let a validator cheat quietly:

  * a bundle is sealed into a round by its PR head SHA and digest *before* any evaluation, and the seal is
    published with the tasks — a validator cannot pick which submission "counted" after seeing results;
  * the withheld half is committed to in the published task and revealed at close with its salt;
  * a PR that appears after the seal is recorded as "late for r, active from r+1" on the PR itself;
  * the crown is the top weight of the *published* close.json, recomputable by anyone.

    SH_STATE=/root/sh/state python -m sh.validator.orchestrate --once      # one round
    SH_STATE=/root/sh/state python -m sh.validator.orchestrate             # forever
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
RESERVED = ("null", "canon")


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


def gh(*args: str, cwd: Path | None = None) -> str:
    return sh(["gh", *args], cwd=cwd)


def _secret(cfg: Config, name: str) -> str:
    return (cfg.state / name).read_text().strip()


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


def seal(cfg: Config, round_id: str, rd: Path) -> dict:
    """Which bundles are in this round: every open `sh:strategy` PR whose lint passed, by head SHA and digest.
    Decided before evaluation and published with the tasks, so it cannot be revised after results."""
    sh(["git", "fetch", "-q", "origin"], cwd=cfg.repo)  # the sealed head SHAs must be readable locally
    prs = json.loads(
        gh(
            "pr",
            "list",
            "--repo",
            REPO,
            "--base",
            BRANCH,
            "--label",
            LABEL_STRATEGY,
            "--state",
            "open",
            "--json",
            "number,headRefOid,headRefName,title",
            "--limit",
            "100",
        )
    )
    active, rejected = {}, {}
    for pr in prs:
        head = pr["headRefOid"]
        bundles = rd / "bundles"
        bundles.mkdir(exist_ok=True)
        # The bundle as of the sealed head SHA — not the branch tip, which the miner may move later.
        listing = sh(["git", "ls-tree", "-r", "--name-only", head, "submissions/"], cwd=cfg.repo, check=False)
        hotkeys = sorted({p.split("/")[1] for p in listing.split() if p.count("/") >= 2})
        if len(hotkeys) != 1:
            rejected[pr["number"]] = f"{len(hotkeys)} submission directories"
            continue
        hotkey = hotkeys[0]
        dest = bundles / hotkey
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True)
        for rel in listing.split():
            if rel.startswith(f"submissions/{hotkey}/"):
                out = dest / rel[len(f"submissions/{hotkey}/") :]
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(sh(["git", "show", f"{head}:{rel}"], cwd=cfg.repo).encode())
        files, problems = collect(dest)
        problems += lint(files)
        if problems:
            rejected[pr["number"]] = problems[0]
            shutil.rmtree(dest, ignore_errors=True)
            continue
        active[hotkey] = {"pr": pr["number"], "head": head, "bundle_sha256": bundle_digest(files)}
    record = {
        "schema": "sh-seal-v2",
        "round_id": round_id,
        "sealed_at": time.time(),
        "active": active,
        "rejected": rejected,
    }
    (rd / "seal.json").write_text(json.dumps(record, indent=1))
    log(rd, "seal", active=len(active), rejected=len(rejected))
    return record


def publish_open(cfg: Config, round_id: str, rd: Path) -> None:
    """The tasks (with their withheld commitments) and the seal, committed where miners can read them."""
    dest = cfg.repo / "rounds" / round_id
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(rd / "tasks", dest / "tasks", dirs_exist_ok=True)
    shutil.copy(rd / "seal.json", dest / "seal.json")
    _commit(
        cfg,
        f"{round_id}: open — {len(list((rd / 'tasks').glob('*.json')))} sealed instances, "
        f"{len(json.loads((rd / 'seal.json').read_text())['active'])} active bundles",
    )
    log(rd, "publish_open")


def _rsync(src: str, dst: str, cfg: Config) -> None:
    sh(["rsync", "-az", "--delete", "-e", f"ssh -o BatchMode=yes -p {cfg.worker_port}", src, dst])


def evaluate(cfg: Config, rd: Path, sealed: dict) -> None:
    """Runs on the GPU worker. The worker gets exactly what an episode needs — tasks, the withheld halves for
    the grader, the checks, the canon and the sealed bundles — and returns the episodes. No credential is ever
    on it; nothing it does needs one."""
    remote = f"{cfg.worker_root}/rounds/{rd.name}"
    sh(["ssh", "-o", "BatchMode=yes", "-p", str(cfg.worker_port), cfg.worker, f"mkdir -p {remote}"])
    for sub in ("tasks", "withheld", "checks", "canon", "bundles"):
        if (rd / sub).exists():
            _rsync(f"{rd / sub}/", f"{cfg.worker}:{remote}/{sub}/", cfg)
    surfaces = ["null", f"canon={remote}/canon"] + [f"{h}={remote}/bundles/{h}" for h in sealed["active"]]
    cmd = (
        f"cd {cfg.worker_root}/pkg && PYTHONPATH={cfg.worker_root}/pkg python3 -m sh.validator.batch "
        f"--round {remote} --surfaces {','.join(surfaces)} --image {cfg.image} --inference unused "
        f"--out {remote}/episodes --concurrency {cfg.concurrency} --network sh-ep "
        f"--tokens {cfg.worker_root}/state/tokens --usage-dir {cfg.worker_root}/state/usage "
        f"> {remote}/batch.log 2>&1; tail -3 {remote}/batch.log"
    )
    sh(["ssh", "-o", "BatchMode=yes", "-o", "ServerAliveInterval=30", "-p", str(cfg.worker_port), cfg.worker, cmd])
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


def announce(cfg: Config, round_id: str, rd: Path, record: dict, sealed: dict) -> str | None:
    """Scorecards on every PR, `scored` on every PR, the crown moved to the top weight. Returns the king."""
    reveal = json.loads((rd / "close" / "reveal.json").read_text())
    (rd / "scorecards").mkdir(exist_ok=True)
    weights = record["weights"]
    king = max(weights, key=weights.get) if weights and max(weights.values()) > 0 else None
    for hotkey, info in sealed["active"].items():
        card = render_scorecard(record, hotkey, reveal)
        (rd / "scorecards" / f"{hotkey}.md").write_text(card)
        body = f"### Round `{round_id}`\n\n" + card
        if hotkey == king:
            body = "👑 **Crowned: top weight this round.**\n\n" + body
        gh("pr", "comment", str(info["pr"]), "--repo", REPO, "--body", body)
        gh("api", "-X", "POST", f"repos/{REPO}/issues/{info['pr']}/labels", "-f", f"labels[]={LABEL_SCORED}")
    # One crown. Remove it wherever it was; place it on the king.
    for pr in json.loads(
        gh("pr", "list", "--repo", REPO, "--label", LABEL_CROWN, "--state", "all", "--json", "number", "--limit", "100")
    ):
        sh(["gh", "api", "-X", "DELETE", f"repos/{REPO}/issues/{pr['number']}/labels/{LABEL_CROWN}"], check=False)
    if king:
        gh(
            "api",
            "-X",
            "POST",
            f"repos/{REPO}/issues/{sealed['active'][king]['pr']}/labels",
            "-f",
            f"labels[]={LABEL_CROWN}",
        )
    # Late arrivals: PRs labelled after the seal are told when they start counting.
    for pr in json.loads(
        gh(
            "pr",
            "list",
            "--repo",
            REPO,
            "--base",
            BRANCH,
            "--label",
            LABEL_STRATEGY,
            "--state",
            "open",
            "--json",
            "number",
            "--limit",
            "100",
        )
    ):
        if pr["number"] not in {i["pr"] for i in sealed["active"].values()} and pr["number"] not in sealed["rejected"]:
            gh(
                "pr",
                "comment",
                str(pr["number"]),
                "--repo",
                REPO,
                "--body",
                f"Arrived after round `{round_id}` was sealed; active from the next round.",
            )
    log(rd, "announce", king=king, scorecards=len(sealed["active"]))
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
    dest = cfg.repo / "rounds" / round_id
    for name in ("close.json", "reveal.json"):
        shutil.copy(rd / "close" / name, dest / name)
    shutil.copytree(rd / "checks", dest / "checks", dirs_exist_ok=True)  # semantics of `custom` predicates
    shutil.copytree(rd / "scorecards", dest / "scorecards", dirs_exist_ok=True)
    shutil.copy(rd / "export" / "manifest.json", dest / "manifest.json")
    (dest / "index.html").write_text(render_leaderboard(record))
    index_path = cfg.repo / "rounds" / "index.json"
    index = (
        json.loads(index_path.read_text()) if index_path.exists() else {"schema": "sh-rounds-index-v2", "rounds": []}
    )
    index["rounds"] = [r for r in index["rounds"] if r["round_id"] != round_id] + [
        {
            "round_id": round_id,
            "closed_at": time.time(),
            "episodes": record["episodes"],
            "king": king,
            "weights": record["weights"],
            "commitments_ok": record["commitments_ok"],
            "hf": exported["upload"].get("url"),
        }
    ]
    index_path.write_text(json.dumps(index, indent=1))
    _commit(
        cfg,
        f"{round_id}: close — king {king or 'none'}, {record['episodes']} episodes, "
        f"{exported['manifest']['sft_rows']} SFT rows, {exported['manifest']['dpo_pairs']} DPO pairs",
    )
    log(rd, "publish_close", king=king)


def _commit(cfg: Config, message: str) -> None:
    sh(["git", "add", "rounds"], cwd=cfg.repo)
    if sh(["git", "status", "--porcelain", "rounds"], cwd=cfg.repo).strip():
        sh(["git", "commit", "-q", "-m", message], cwd=cfg.repo)
        sh(["git", "pull", "-q", "--rebase", "origin", BRANCH], cwd=cfg.repo, check=False)
        sh(["git", "push", "-q", "origin", BRANCH], cwd=cfg.repo)


# ─── the round, and the loop ───────────────────────────────────────────────────────────────────────
def run_round(cfg: Config) -> dict:
    round_id = next_round_id(cfg)
    rd = cfg.rounds / round_id
    rd.mkdir(parents=True)
    log(rd, "start")
    mint(cfg, round_id, rd)
    sealed = seal(cfg, round_id, rd)
    publish_open(cfg, round_id, rd)
    evaluate(cfg, rd, sealed)
    record = close(cfg, round_id, rd)
    king = announce(cfg, round_id, rd, record, sealed)
    exported = export_and_upload(cfg, round_id, rd)
    publish_close(cfg, round_id, rd, record, king, exported)
    (rd / "DONE").write_text(json.dumps({"king": king, "weights": record["weights"]}))
    log(rd, "done", king=king)
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
    while True:
        try:
            result = run_round(cfg)
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
