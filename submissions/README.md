# Submissions

One directory per hotkey, containing **prose only** — the strategy your agent runs under:

```
submissions/<your-hotkey>/
  SOUL.md                              the identity and rules the agent operates by
  skills/<name>/SKILL.md               optional; frontmatter `name` must match the directory
  skills/<name>/references/*.md        optional; loaded only when the agent opens the skill
```

Nothing else is accepted. No scripts, no config, no URLs, no `!\`…\`` inline shell, no `${HERMES_…}`.
A strategy is instructions for the agent, not code that runs — the validator executes *its* pinned agent and
model against your prose, which is what makes every submission comparable.

## Before you open a pull request

```sh
python -m sh.cli.lint submissions/<your-hotkey>
```

It prints the same verdict CI will, plus your `bundle_sha256` — the digest your on-chain commitment is made
over. One submission directory per pull request.

## What happens next

1. **Lint** runs on your PR automatically (`.github/workflows/sh-strategy-lint.yml`). It is the whole of what
   CI does: no code from a submission is ever executed in this repository.
2. **Evaluation** happens on the validator, not here. Your bundle runs as a *surface* against the round's sealed
   instances, through the same runner, sandbox and grader as the NULL and CANON reference arms.
3. **Scoring** compares you to the baseline on the same instances — passing a task is not the achievement,
   beating the pinned model without your prose is. See `docs/` for the scoring definition.
4. **The scorecard** is posted back to your PR when the round closes, together with the revealed withheld half
   so you can check the grading yourself.
