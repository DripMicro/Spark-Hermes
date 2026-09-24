# Submissions

A round opens with a **2-hour submission window**. During the window you fetch the round's tasks, write a strategy,
and submit it as one signed pull request per hotkey; you may resubmit as often as you like
and each submission replaces the last. When the window closes the validator seals every open strategy PR at
its head SHA, evaluates, scores, crowns, and opens the next round. Nothing submitted after the close is sealed. If the
window closes with no valid submission (an incumbent alone does not count), the round is not sealed: it reopens with the same tasks and a fresh window.

**Private submissions.** Once the board advertises a submission server (`submit_server` in `docs/live/live.json`),
the CLI switches over by itself: your prose is uploaded to that server and your pull request carries only your
signed commitment (`attestation.json`), so no rival can read your strategy while the window is open. The validator
then fetches your bundle by the digest your commitment names. Your prose becomes public only after the round is
scored — a losing bundle at that round's close, the crowned one only once it is dethroned. While a server is
advertised — as it has been since r0005 — a pull request that adds anything under your directory besides
`attestation.json` (and the server's `receipt.json`) is refused, by CI and at the seal: prose in a PR is public the
moment it is opened. Only a hotkey registered on SN74 can upload. With no server advertised, the bundle itself goes
in the pull request, as described above.

The tasks are real bugs in real Python repositories (family `swe_fix`, from SWE-smith): a problem statement, the
repository at the bug, and a grader that runs the tests the bug broke — each passing test earns its share of the
task's credit, and none counts if a test that passed before now fails. What `tasks` gives you are **practice
bugs**: one per hidden bug, from the same repository and environment as that bug (a repository can appear twice),
with its SWE-smith instance id so you can reproduce it locally. The round is scored on **6 different, hidden bugs**
from those same repositories, published when it closes. Write how to debug these codebases; the answers to the practice bugs will not be asked.

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

The lint also bounds the bundle: a `SKILL.md` at most 15 KiB, any file at most 64 KiB, the bundle at most 512 KiB,
UTF-8 text only (no CRLF, no symlinks), a skill `description` of at most 500 characters, no agent-generated markers,
no reserved names. `python -m sh.cli.lint DIR` reports every rule by its L-code.

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
repository. Resubmit as often as you like during the window; each push replaces your PR. The PR's author is your
public face: the board and the round pages show that GitHub account's avatar and `@login` beside your hotkey, and it
is recorded in `rounds/index.json` at close — submit from an account you are willing to show. Resubmitting from the
incumbent's own hotkey replaces its carried bundle at the seal (a byte-identical resubmission is skipped by the CLI).

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
  writing outside the workspace; any network attempt; reading the grader's or the withheld paths; an inline-shell
  marker or a task's instance id in the bundle; filling the worker's disk (`disk_abuse`); or a fix that reaches for
  the test runner or Python's import machinery (`harness_tamper`). Two disqualified episodes in the pooled window
  zero the whole score. Running out of the token budget or hitting a backstop is **not** a disqualification — the
  episode scores what it achieved. Fix the source, run the tests, stop.
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

**Win the crown.** The reward follows your crowned pull request being merged, through the Gittensor workflow — so
what you are competing for each round is the crown, and the bar for it is concrete: the **best mean Δ vs the
baseline on that round's instances**, above zero, over at least **4 instances** shared with the baseline, with no
disqualification. One good round wins it; you do not need a run of them.

The crown is decided on **this round alone**, so a round is always winnable no matter how you did before. The
incumbent's bundle stays in `submissions/` until a challenger is crowned over it, its pooled window says it is
worse than the baseline, or it goes three rounds without the crown (see step 4 below).

**What the pooled columns mean.** They look at your last 8 rounds together, not just this one.

- **score** — how much better than the baseline you are, on average: the share of checks you passed minus the
  share the baseline passed *on the same instances*, after the overfit and copy penalties. `+0.076` means you
  passed 7.6 points more of the checks than the baseline did. Below zero means worse than the baseline.
- **weight** — your share among the strategies whose score is above zero; the shares sum to 1. It is 0 only if
  you are not above the baseline, your window is too thin (fewer than 8 episodes), or a penalty applies — and
  the board says which.
- **Δc** — the one-sided 90 % lower bound of your score: how sure the gain is. Small windows make it
  conservative; it is a confidence figure, not a second score.

Open any board row to see the per-instance credits every one of these numbers is made of.

## What happens next

1. **Lint** runs on your PR automatically — and, with private submissions, on the server when you upload, which
   also refuses an answer-copy. It is the whole of what CI does: no code from a submission is ever executed in
   this repository.
2. **Seal**, when the window closes: one PR per hotkey — the **latest *signed*** counts, not the newest PR (what
   you signed is public, so a newer PR carrying your old bundle cannot displace your real one). With private
   submissions the validator fetches your revealed bundle by the digest your commitment names and re-checks it.
   Your PR must change only your own `submissions/<hotkey>/` directory and nothing else, or it is rejected.
3. **Evaluation** on the validator's GPU, inside the sealed sandbox, against the strategy-less NULL baseline on
   the same instances (the CANON reference strategy runs every 8th round, for calibration). The board shows
   progress live.
4. **Crown**: the strategy with the best Δ vs baseline *on this round's instances* — if it beat the baseline —
   is labelled `sh:<round>:crown` (e.g. `sh:r0001:crown`), merged into `submissions/`, and defends as the incumbent next round. Every
   other competition PR is closed with the reason. **The reward follows a merged PR, so a king is paid for a round it
   defends only if it opened a defense PR in that round's window:** run the CLI's `submit` again with the crowned bundle
   unchanged. That PR carries only a fresh `attestation.json` for the round, over the same digest; the seal treats it as
   the incumbent (ties still go to it, and it is not a new bundle that could cost the crown), and if the crown holds,
   that PR is merged and labelled. A king that opens no defense PR still defends, but a round it wins pays nothing. The incumbent is **dethroned** (removed from `submissions/`)
   only when a challenger is crowned over it, when its pooled 8-round window says it is worse than the baseline
   (the correctness gate fails on enough evidence), or after 3 rounds in a row without the crown — a single
   round that crowns nobody does not unseat it.
5. **Payment** pools the last 8 rounds: Δc, the lower bound of your Δ vs baseline, is what earns weight.
   Consistency pays; a single round does not.
6. **Your scorecard** is posted on the PR with the revealed withheld halves and salts, so you can recompute the
   grading yourself; every out-of-competition bundle's prose is published under `rounds/<round>/revealed/` so you
   can match its committed digest against its content. The definition of the score is `sh/scoring/v2.py`; the crown
   rule is `sh/scoring/crown.py`; what they run against is `docs/pins.md`.
