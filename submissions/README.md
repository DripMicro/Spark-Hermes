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
reproduce it locally. The round is scored on **as many different, hidden bugs** (up to 8) from those same
repositories, published when it closes. Write how to debug these codebases; the answers to the practice bugs will not be asked.

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
round's fixes (the code its hidden bugs replaced) is refused at seal (S1) — write how to work, not what to type. The validator executes *its* pinned
agent and model against your prose, which is what makes every submission comparable.

## The loop, as a miner

**Once:** fork `gittensor-model-hub/Spark-Hermes` on GitHub, clone your fork, authenticate `gh`, and sync deps.

```sh
gh repo fork gittensor-model-hub/Spark-Hermes --clone && cd Spark-Hermes
gh auth login                                             # the CLI opens and updates your PR through gh
uv sync                                                   # once; run everything below through `uv run`
```

**Each round** (all commands `uv run …`, because stock Python lacks the deps):

```sh
uv run python -m sh.cli.miner tasks                       # this round's practice bugs -> tasks/<round>/
$EDITOR my-strategy/SOUL.md                               # write how to fix bugs in those repositories
uv run python -m sh.cli.lint my-strategy                  # the same check CI runs
uv run python -m sh.cli.miner submit --bundle my-strategy --key ~/.bittensor/wallets/<cold>/hotkeys/<hot> \
        --checkout . --head-owner <your github user>      # opens, or replaces, your PR for this round
uv run python -m sh.cli.miner status --hotkey <ss58>
```

`--head-owner` is your GitHub user: the branch is pushed to your fork and the PR opened against the competition
repository. Resubmit as often as you like during the window; each push replaces your PR.

`submit` signs `spark-hermes:<repo>:<round>:<bundle_sha256>:<signed_at>` with your hotkey (sr25519) and writes
`attestation.json`; your most recently signed submission is the one that counts.
The seal accepts a PR only if the signature is your hotkey's, over *this* round and *this* digest, and the
directory is named after the hotkey — a PR cannot be replayed into another round or altered after signing.

## What you're scored on

- **Credit** per hidden bug: the share of the tests the bug broke that pass after your run, and **0 if any test
  that passed before now fails**. Your round score is your mean credit minus the strategy-less baseline's, on the
  same bugs.
- **The sandbox the agent runs in:** the repository at `/testbed` (git history cut to one commit; the broken
  tests are removed from its tree), tools **`terminal` and `file` only**, **no network**, a **token budget of
  600,000** prompt+completion tokens (the run ends when it is spent), and backstops of **100 turns / 30 minutes**.
- **Disqualifications (credit 0):** modifying or adding tests or test configuration; editing a protected file;
  writing outside the workspace; any network attempt; or a fix that reaches for the test runner or Python's import
  machinery (`harness_tamper`). Fix the source, run the tests, stop.
- **S1:** a bundle that reproduces a bug's fix (the code it replaced) is refused. Do not paste upstream source
  into `references/`; describe how to debug, not what to type.

## Reproduce a practice bug locally

Each practice bug names its SWE-smith `instance_id` and environment image. To run it as the validator would:

```sh
docker pull <environment image from the preview>          # ~1.5 GB, amd64
# in the container: git fetch origin <instance_id> && git checkout <instance_id>
# the branch has the bug and its breaking tests removed; the fix is the reverse of the dataset `patch`
```

The full dataset (patches, FAIL_TO_PASS / PASS_TO_PASS) is `SWE-bench/SWE-smith` on Hugging Face.

## Getting paid

Weight is set on Bittensor **SN74** for registered hotkeys. Payment pools the **last 8 rounds** and needs at
least **8 scored episodes** in that window, so your first round or two accumulate evidence before they pay —
consistency across rounds is what earns weight, not one lucky round.

## What happens next

1. **Lint** runs on your PR automatically. It is the whole of what CI does: no code from a submission is ever
   executed in this repository.
2. **Seal**, when the window closes: one PR per hotkey — the **latest *signed*** counts, not the newest PR (signed
   bundles are public, so a newer PR carrying your old bundle cannot displace your real one). Your PR must change
   only your own `submissions/<hotkey>/` directory and nothing else, or it is rejected.
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
