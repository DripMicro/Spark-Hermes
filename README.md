# Spark-Hermes

**One pinned agent. A competition on how it is instructed. Every result checkable by a stranger.** SN74 Gittensor.

A strategy is prose — a `SOUL.md` and optional skills — and nothing else. The validator runs the same pinned Hermes
agent and model under every strategy, in a sealed sandbox, on task instances whose grading criteria were committed
before submissions opened. A strategy is paid for beating the strategy-less baseline on the same instances. The
crowned strategy is merged as the incumbent; every verified trajectory is exported as training data.

- **Live:** https://gittensor-model-hub.github.io/Spark-Hermes/live/
- **Submit:** [`submissions/README.md`](submissions/README.md)
- **Pins:** [`docs/pins.md`](docs/pins.md) · **Findings:** [`docs/spikes.md`](docs/spikes.md)
- **Training data:** [`gittensor-model-hub/spark-hermes-rounds`](https://huggingface.co/datasets/gittensor-model-hub/spark-hermes-rounds)

## Layout

| Path | What |
|---|---|
| `sh/validator/` | the round loop (`orchestrate.py`), episode runner and sealed sandbox, grader, inference proxy, batch runner |
| `sh/scoring/` | scoring v2: paired delta against the baseline, one-sided lower bound, gated efficiency |
| `sh/predicates/` | the closed predicate vocabulary tasks are graded with; copied into the runner image at build |
| `sh/exports/` | SFT rows and DPO pairs from a closed round, leak scan, Hugging Face upload |
| `sh/cli/` | `lint` (the submission contract, the same check CI runs), `scorecard`, `mock_miners` |
| `sh/web/` | the static page for a closed round |
| `submissions/` | one directory per hotkey, prose only — merged when crowned |
| `rounds/` | every round's tasks, seal, `close.json`, `reveal.json`, checks, scorecards, `index.json` |
| `docs/` | the site served by Pages: landing, live dashboard, round pages; pins and findings |

Task families and their withheld halves live in a private repository; only what a round publishes is here.

## Compete

```sh
mkdir -p submissions/<hotkey> && $EDITOR submissions/<hotkey>/SOUL.md
python -m sh.cli.lint submissions/<hotkey>        # ok, plus your bundle_sha256
git checkout -b miner/<hotkey> && git add submissions/<hotkey> && git commit -m "miner: <hotkey>"
gh pr create --base sh/v2-pipeline
```

The next round labels every open PR that touches `submissions/` `sh:strategy`, seals it by head SHA, evaluates it, and posts the scorecard on the PR. The
crowned PR is merged; the others are closed with the round — resubmit to compete again.

## Run the validator

```sh
uv sync --extra dev
HF_TOKEN=... uv run python -m sh.validator.orchestrate --tasks 8 --difficulty 3 --window 8      # forever; --once for one round
uv run python -m sh.validator.orchestrate --help
```

The control plane (credentials, GitHub, Hugging Face) stays on the machine you run this on; episodes run on a GPU
worker over ssh and rsync, inside `sh/validator/images/` built at the pinned Hermes commit. `HF_TOKEN` is the only
secret, read from the environment and never from a file. A restarted loop resumes an unfinished round from the stage
it reached and never changes what that round sealed.

## Check a round

`rounds/<id>/reveal.json` carries every withheld half and salt. For each instance,
`"hmac-sha256:" + HMAC(salt, canonical_json(withheld))` must equal the commitment published in `rounds/<id>/tasks/`
when the round opened, and `close.json` recomputes from the graded episodes. Nothing here needs to be trusted.

## Develop

```sh
uv run ruff check . && uv run ruff format --check . && uv run pyright && uv run pytest -q
```

MIT. Preserve the upstream licenses of the pinned model and of [Hermes Agent](https://github.com/NousResearch/hermes-agent).
