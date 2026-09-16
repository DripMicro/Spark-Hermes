# Submissions

A round opens with a **2-hour submission window**. During the window you fetch the round's tasks, write a strategy,
and submit it as one signed pull request per hotkey; you may resubmit as often as you like
and each submission replaces the last. When the window closes the validator seals every open strategy PR at
its head SHA, evaluates, scores, crowns, and opens the next round. Nothing submitted after the close is sealed. If the
window closes with no valid submission, the round is not sealed: it reopens with the same tasks and a fresh window.

The tasks are real bugs in real Python repositories (family `swe_fix`, from SWE-smith): a problem statement, the
repository at the bug, and a grader that runs the tests the bug broke — each passing test earns its share of the
task's credit, and none counts if a test that passed before now fails. What `tasks` gives you are **practice
bugs**: one from each repository and environment the round is scored on, with its SWE-smith instance id so you can
reproduce it locally. The round is scored on **8 different, hidden bugs** from those same repositories, published
when it closes. Write how to debug these codebases; the answers to the practice bugs will not be asked.

## What a strategy is

Prose only — the instructions the pinned Hermes agent runs under:

```
submissions/<hotkey>/
  SOUL.md                              the identity and rules the agent operates by
  skills/<name>/SKILL.md               optional; frontmatter `name` must match the directory
  skills/<name>/references/*.md        optional; loaded only when the agent opens the skill
  attestation.json                     written by the CLI: your hotkey's signature over this round and this bundle
```

No scripts, no config, no URLs, no `!\`…\`` inline shell, no `${HERMES_…}`. And not the round's answers: a bundle that reproduces the
round's reference solutions or verifiers is refused at seal (S1) — write how to work, not what to type. The validator executes *its* pinned
agent and model against your prose, which is what makes every submission comparable.

## The loop, as a miner

```sh
uv sync                                                   # once
python -m sh.cli.miner tasks                              # this round's practice bugs -> tasks/<round>/  (only this round exists)
$EDITOR my-strategy/SOUL.md                               # write how to fix bugs in those repositories
python -m sh.cli.lint my-strategy                         # the same check CI runs
python -m sh.cli.miner submit --bundle my-strategy --key ~/.bittensor/wallets/<cold>/hotkeys/<hot> \
        --checkout . --head-owner <your github user>      # opens, or replaces, your PR for this round
python -m sh.cli.miner status --hotkey <ss58>
```

`submit` signs `spark-hermes:<repo>:<round>:<bundle_sha256>:<signed_at>` with your hotkey (sr25519) and writes
`attestation.json`; your most recently signed submission is the one that counts.
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
