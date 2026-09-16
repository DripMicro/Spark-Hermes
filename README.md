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
| `sh/scoring/` | `v2.py` — payment: paired delta against the baseline over the pooled window, one-sided lower bound; `crown.py` — the crown, on this round alone |
| `sh/predicates/` | the closed predicate vocabulary tasks are graded with; copied into the runner image at build |
| `sh/exports/` | the king's SFT rows and DPO pairs from a closed round, leak scan, Hugging Face upload |
| `sh/cli/` | `miner` (tasks / submit / status), `lint` (the contract CI runs), `attest` (the hotkey's signature), `scorecard`, `mock_miners` |
| `sh/web/` | the static page for a closed round |
| `submissions/` | one directory per hotkey, prose only — merged when crowned |
| `rounds/` | every round's tasks, window, seal, `close.json`, `crown.json`, `reveal.json`, checks, scorecards; `queue.json` — digests of rounds minted ahead |
| `docs/` | the site served by Pages: landing, live dashboard, round pages; pins and findings |

Task families and their withheld halves live in a private repository; only what a round publishes is here.

## Compete

A round opens with 8 tasks and a 2-hour submission window; the board shows the countdown.

```sh
python -m sh.cli.miner tasks                                   # this round's tasks; nothing else exists to fetch
$EDITOR my-strategy/SOUL.md                                    # prose for those tasks
python -m sh.cli.miner submit --bundle my-strategy --key ~/.bittensor/wallets/<cold>/hotkeys/<hot> \
        --checkout . --head-owner <your github user>           # one signed PR per hotkey; resubmit to replace
```

When the window closes the validator seals every strategy PR at its head SHA, evaluates, and posts the scorecard
on the PR. The best Δ vs baseline on this round's instances is crowned and merged; the rest are closed; the next
round opens at once. Payment pools the last 8 rounds. Details: [`submissions/README.md`](submissions/README.md).

## Run the validator

```sh
uv sync --extra dev
SH_SALT_SECRET=... DOCKER_HOST=ssh://<worker> python -m supply.queue --queue queue --plan terminal_task:8:1 --ahead 3   # private repo: mints rounds ahead, images built on the worker
HF_TOKEN=... uv run python -m sh.validator.orchestrate --queue ../Spark-Hermes-Withheld/queue       # forever; --once for one round
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
