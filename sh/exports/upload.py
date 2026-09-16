"""Upload a closed round's training data to Hugging Face (spec §8, V7).

One private dataset repo, partitioned by round: `rounds/<round_id>/{sft.jsonl,dpo.jsonl,manifest.json}` plus a
top-level `index.json` and a dataset card. Idempotent — a round already present with the same manifest digest
is skipped, so the loop can call this every round without duplicating anything.

Two refusals, both deliberate:

  * **Nothing uploads without a leak scan having run.** The manifest records the scan; a manifest without it is
    refused. The withheld half is what makes every future round gradeable, and it must never leave in a row.
  * **The token comes from the environment, never from a file in a repository.** `HF_TOKEN` only.

    HF_TOKEN=... python -m sh.exports.upload --export DIR --repo gittensor-model-hub/spark-hermes-rounds
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

CARD = """---
license: other
pretty_name: Spark-Hermes rounds
tags: [agent, hermes, trajectories, sft, dpo]
---

# Spark-Hermes rounds

Training data from a competition in which miners submit **prose strategies** and a validator runs one pinned
agent and model against every strategy inside a sealed sandbox. Every row here is an episode that a **withheld**
half verified — grading criteria committed to before submissions opened and revealed at close — so a row says
"this trajectory actually solved the task", not "this trajectory looked right".

Layout: `rounds/<round_id>/sft.jsonl`, `rounds/<round_id>/dpo.jsonl`, `rounds/<round_id>/manifest.json`, and
`index.json` listing every round. The public round artefacts (tasks, revealed withheld halves, scores,
leaderboard) live in the subnet repository under `rounds/<round_id>/`.
"""


def _api(token: str):
    from huggingface_hub import HfApi

    return HfApi(token=token)


def upload(export_dir: Path, repo: str, token: str, *, round_id: str | None = None) -> dict:
    manifest = json.loads((export_dir / "manifest.json").read_text())
    if not manifest.get("leak_scan"):
        raise SystemExit("refusing to upload: the manifest records no leak scan")
    round_id = round_id or manifest.get("round_id") or export_dir.name
    api = _api(token)
    api.create_repo(repo, repo_type="dataset", private=True, exist_ok=True)

    # Idempotence: the same round with the same manifest digest is already there.
    index: dict = {"schema": "sh-hf-index-v2", "rounds": {}}
    try:
        raw = api.hf_hub_download(repo, "index.json", repo_type="dataset", token=token)
        index = json.loads(Path(raw).read_text())
    except Exception:
        pass
    key = f"{manifest.get('sft_sha256')}:{manifest.get('dpo_sha256')}"
    if index["rounds"].get(round_id, {}).get("key") == key:
        return {"repo": repo, "round_id": round_id, "uploaded": False, "reason": "already present, same digests"}

    prefix = f"rounds/{round_id}"
    for name in ("sft.jsonl", "dpo.jsonl", "manifest.json"):
        api.upload_file(
            path_or_fileobj=str(export_dir / name),
            path_in_repo=f"{prefix}/{name}",
            repo_id=repo,
            repo_type="dataset",
            commit_message=f"{round_id}: {name}",
        )
    index["rounds"][round_id] = {
        "key": key,
        "sft_rows": manifest.get("sft_rows"),
        "dpo_pairs": manifest.get("dpo_pairs"),
        "families": manifest.get("families"),
    }
    api.upload_file(
        path_or_fileobj=json.dumps(index, indent=1).encode(),
        path_in_repo="index.json",
        repo_id=repo,
        repo_type="dataset",
        commit_message=f"{round_id}: index",
    )
    api.upload_file(
        path_or_fileobj=CARD.encode(),
        path_in_repo="README.md",
        repo_id=repo,
        repo_type="dataset",
        commit_message="dataset card",
    )
    return {
        "repo": repo,
        "round_id": round_id,
        "uploaded": True,
        "sft_rows": manifest.get("sft_rows"),
        "dpo_pairs": manifest.get("dpo_pairs"),
        "url": f"https://huggingface.co/datasets/{repo}/tree/main/{prefix}",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--round-id")
    a = ap.parse_args(argv)
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        print("HF_TOKEN is not set", file=sys.stderr)
        return 2
    print(json.dumps(upload(Path(a.export), a.repo, token, round_id=a.round_id), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
