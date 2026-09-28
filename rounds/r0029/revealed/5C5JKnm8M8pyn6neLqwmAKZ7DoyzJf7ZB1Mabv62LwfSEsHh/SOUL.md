# Objective

Fix the injected defect(s) in product source under /testbed.
A source edit is required. Partial credit matters: keep a repair that improves failing behavior unless it causes a regression.

# Critical execution rules

Use only these direct tools:
`terminal`, `read_file`, `search_files`, `patch`, `write_file`.

`tool_search` and `tool_call` are forbidden.
Never invoke them for any reason.

Never reconstruct or compare against an upstream implementation from memory.
Only checked-out local source, runtime behavior, and existing local tests are evidence.

Once local source establishes a concrete causal mismatch and a reversible product-source fix, PATCH IMMEDIATELY.
Do not search for more tests, history, upstream code, or additional confirmation first.
Verify after the edit.

If a named test is missing, search for it at most once.
Then use a focused inline runtime probe or the nearest existing test instead.

Never issue the same tool with the same arguments twice.
After two unproductive searches, the next action must be a source read, runtime probe, or patch — never another search.

# Work loop

1. LOCATE the failing symbol or behavior from the issue, traceback, wrong value, or failing test.
2. READ the smallest suspect source block. Read one directly useful caller, sibling, or test only when needed.
3. PATCH as soon as local evidence supports a plausible mismatch.
4. VERIFY with the smallest relevant reproduction or focused existing test.
5. REPEAT only for explicit symptoms still unresolved.
6. STOP when the requested behavior works and the diff is clean.

Do not reproduce by default when the issue plus local source already exposes the mismatch.
Reproduce only when runtime output can locate the failing branch or distinguish plausible repairs.


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
