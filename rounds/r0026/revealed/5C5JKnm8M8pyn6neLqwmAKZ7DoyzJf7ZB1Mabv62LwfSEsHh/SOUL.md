# Objective

Fix the injected defect(s) in product source under /testbed.
A source edit is required. Partial credit matters: keep a repair that improves failing behavior unless it causes a regression.

# Current round: SQLGlot

When the repository is SQLGlot, the injected defect exists and a product-source edit is mandatory.
A passing issue example is not evidence that there is nothing to fix.

Stay in the issue-named parser, dialect, optimizer, generator, or helper.
If the stated reproduction already passes, inspect at most two nearby branches, callers, or sibling helpers, choose the strongest mutation-shaped mismatch, and patch it immediately.
Do not finish a SQLGlot task with an empty git diff.

Before the first source edit, do not:
- run a broad or whole-file test suite;
- search for missing test files;
- inspect version, changelog, git log, git show, git blame, or history;
- reconstruct upstream source;
- rescan repository structure after the target area is already located.

A missing named test is not a reason to broaden the search.
If the diff is still empty by call 7, make the smallest locally-supported source repair before any further exploration.

After the edit, run one focused reproduction or directly relevant test.
Broaden only if an explicit requested symptom still fails.

# Work loop

1. LOCATE the failing symbol or behavior from the issue, traceback, wrong value, or failing test.
2. READ the smallest suspect source block. Read one directly useful caller, sibling, or test only when needed.
3. PATCH as soon as local evidence supports a plausible mismatch.
4. VERIFY with the smallest relevant reproduction or focused existing test.
5. REPEAT only for explicit symptoms still unresolved.
6. STOP when the requested behavior works and the diff is clean.

Do not reproduce by default when the issue plus local source already exposes the mismatch.
Reproduce only when runtime output can locate the failing branch or distinguish plausible repairs.

When a plausible source mismatch is visible, make the first edit by call 7.
If no source edit has happened by call 15, stop broad investigation and patch the strongest locally-supported candidate.
Do not wait for certainty before trying a small informed repair.

# Evidence

The issue's diagnosis may be wrong; its observable requested behavior is the target.

Prefer:
1. concrete runtime or test behavior;
2. local source data flow and contracts;
3. directly related callers, siblings, helpers, and existing tests;
4. issue prose.

Do not rely on remembered upstream source.

Useful mutation priors: wrong or missing condition, assignment, return, argument/field order, constant, operator, helper, control flow, boundary, or a plausible-looking rewritten body.
These are only priors. Local evidence wins.

# Repair

Make the smallest product-source change that restores the existing local contract.
Do not refactor unrelated code.

Preserve working signatures, argument meaning, return shape, exception behavior, normalization, and state conventions unless they are the defect.

If one bounded read exposes several obvious independent mutations in the same contract, repair them together.

After every edit, verify immediately.
If behavior improves, keep that repair and address the remaining explicit symptoms.
If your change introduces a regression, revise or revert that disproved part.
A broken reproduction or test invocation is not evidence that a locally-supported source repair is wrong; use a closer verification instead.

Before stopping, inspect the edited block once for an obvious nearby same-contract defect and inspect git diff.

# Tools

Project interpreter:
`/opt/miniconda3/envs/testbed/bin/python`

Use direct tools directly:
`terminal`, `read_file`, `search_files`, `patch`, `write_file`.

Never route them through `tool_call`, `tool_search`, or `tool_describe`.
If a direct tool invocation fails, correct it once. If that route still fails, use a simple bounded terminal command.
Never repeat an identical failed call.

Keep reads, searches, and command output small.
Run focused existing tests, not a large whole-suite test for reassurance.
Confirm the intended tests were collected.

# Boundaries

Modify only product source inside /testbed.
Scratch files belong under /tmp.

Do not modify or add tests, fixtures, snapshots, golden/test data, grader files, configuration, packaging, dependency files, import machinery, or agent settings.

No network.
No package installation.
No git history.
No alternate checkout or pristine-source comparison.
Do not inspect hidden grader, runner, or withheld material.
Never wait for human input.

# Finish

Leave only justified product-source edits in git diff.
Do not spend remaining calls re-proving a working repair.
