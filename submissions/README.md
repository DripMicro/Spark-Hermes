# Submissions

A round opens with 8 tasks and a **2-hour submission window**. During the window you fetch the tasks, write a
strategy for them, and submit it as one signed pull request per hotkey; you may resubmit as often as you like
and each submission replaces the last. When the window closes the validator seals every open strategy PR at
its head SHA, evaluates, scores, crowns, and opens the next round. Nothing submitted after the close is sealed. If the
window closes with no valid submission, the round is not sealed: it reopens with the same tasks and a fresh window.

## What a strategy is

Prose only — the instructions the pinned Hermes agent runs under:

```
submissions/<hotkey>/
  SOUL.md                              the identity and rules the agent operates by
  skills/<name>/SKILL.md               optional; frontmatter `name` must match the directory
  skills/<name>/references/*.md        optional; loaded only when the agent opens the skill
  attestation.json                     written by the CLI: your hotkey's signature over this round and this bundle
```

No scripts, no config, no URLs, no `!\`…\`` inline shell, no `${HERMES_…}`. The validator executes *its* pinned
agent and model against your prose, which is what makes every submission comparable.

## The loop, as a miner

```sh
uv sync                                                   # once
python -m sh.cli.miner tasks                              # this round's tasks -> tasks/<round>/  (only this round exists)
$EDITOR my-strategy/SOUL.md                               # write for those tasks
python -m sh.cli.lint my-strategy                         # the same check CI runs
python -m sh.cli.miner submit --bundle my-strategy --key ~/.bittensor/wallets/<cold>/hotkeys/<hot> \
        --checkout . --head-owner <your github user>      # opens, or replaces, your PR for this round
python -m sh.cli.miner status --hotkey <ss58>
```

`submit` signs `spark-hermes:<round>:<bundle_sha256>` with your hotkey (sr25519) and writes `attestation.json`.
The seal accepts a PR only if the signature is your hotkey's, over *this* round and *this* digest, and the
directory is named after the hotkey — a PR cannot be replayed into another round or altered after signing.

## What happens next

1. **Lint** runs on your PR automatically. It is the whole of what CI does: no code from a submission is ever
   executed in this repository.
2. **Seal**, when the window closes: one PR per hotkey (the newest counts), labelled `sh:round:<id>`.
3. **Evaluation** on the validator's GPU, inside the sealed sandbox, against the NULL and CANON reference arms
   on the same instances. The board shows progress live.
4. **Crown**: the strategy with the best Δ vs baseline *on this round's instances* — if it beat the baseline —
   is labelled `sh:round:crown`, merged into `submissions/`, and defends as the incumbent next round. Every
   other competition PR is closed with the reason.
5. **Payment** pools the last 8 rounds: Δc, the lower bound of your Δ vs baseline, is what earns weight.
   Consistency pays; a single round does not.
6. **Your scorecard** is posted on the PR with the revealed withheld halves and salts, so you can recompute the
   grading yourself. The definition of the score is `sh/scoring/v2.py`; the crown rule is `sh/scoring/crown.py`;
   what they run against is `docs/pins.md`.
