"""Upload a closed round's training data to Hugging Face (spec §8, V7).

One public dataset repo, partitioned by round: `rounds/<round_id>/{sft.jsonl,dpo.jsonl,manifest.json}` plus a
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

# The `configs` block is what makes the dataset viewer work. Without it the viewer globs every file into one split
# — sft.jsonl, dpo.jsonl, manifest.json and index.json all at once — and the incompatible schemas raise a CastError,
# which switches the viewer off for the whole repository. Two configs, each naming only its own rows.
CARD = """---
license: mit
pretty_name: Spark-Hermes rounds
tags: [agent, hermes, trajectories, sft, dpo, swe-bench]
configs:
  - config_name: sft
    default: true
    data_files:
      - split: train
        path: rounds/*/sft.jsonl
  - config_name: dpo
    data_files:
      - split: train
        path: rounds/*/dpo.jsonl
---

# Spark-Hermes rounds

Training data from a competition (Bittensor SN74) in which miners submit **prose strategies** and a validator
runs one pinned agent (Hermes) and model (Qwen3.8-27B) against every strategy inside a sealed sandbox. The tasks
are bug fixes drawn from [SWE-bench/SWE-smith](https://huggingface.co/datasets/SWE-bench/SWE-smith) (MIT).

Only the **crowned** strategy of each round is exported. **SFT** rows are its episodes that a withheld test suite
verified fully. **DPO** pairs a higher-credit episode (chosen, ≥ 0.8 of the tests) against a lower-credit one on
the same task — chosen rows are strong, not necessarily perfect. Grading criteria were committed to before
submissions opened and revealed at close.

Two configs: **`sft`** (`conversations`, `tools`, `verified_success`, …) and **`dpo`** (`prompt`, `chosen`,
`rejected`, …). Load one at a time:

```python
from datasets import load_dataset
sft = load_dataset("gittensor-model-hub/spark-hermes-rounds", "sft", split="train")
dpo = load_dataset("gittensor-model-hub/spark-hermes-rounds", "dpo", split="train")
```

Layout: `rounds/<round_id>/{sft.jsonl,dpo.jsonl,manifest.json}` and `index.json` listing every round (the two JSON
files are metadata, outside both configs). The public round artefacts (tasks, revealed withheld halves, scores,
leaderboard) live in the subnet's GitHub repository under `rounds/<round_id>/`. Upstream repositories keep their
own licenses; see each row's `source`.
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
    api.create_repo(
        repo, repo_type="dataset", private=False, exist_ok=True
    )  # public: this is the point — training data

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
