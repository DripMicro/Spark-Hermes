# Repair the injected bug

Fix the broken production source in /testbed.
Do not edit tests, grading files, or project configuration.
Do not use network access or repository history.

Use these direct tools exactly as provided:
terminal, read_file, search_files, patch, write_file.

Do not use tool_search or tool_call.
If a direct tool call fails because of its arguments, correct it once.
If it fails again, use terminal instead of searching for another tool.

Use the project interpreter when Python is needed:
`/opt/miniconda3/envs/testbed/bin/python`.

Success is an applied production-source repair whose behavior has been checked.
Investigation without an edit is not completion.

Partial correct repairs are valuable.
Keep a verified repair even if another symptom remains.
A regression is worse than leaving an unsupported symptom unresolved.

## Work loop

LOCATE -> READ -> PATCH OR REPRODUCE -> VERIFY -> NEXT SYMPTOM -> STOP

Start from the symbol, traceback, failing behavior, or example named by the task.

Use one narrow search to locate the responsible code.
Read the smallest complete function or local region needed to reason about the failure.
Read an immediate caller or sibling only when it answers a specific unresolved question.

Do not reconstruct upstream source from memory.
Checked-out local source, runtime behavior, surviving tests, callers, siblings,
and local documentation are evidence.

If a narrow search naturally exposes generated local documentation or a local
reference copy of the same source, compare it once before reconstructing the
behavior from scratch. Do not search proactively for such copies.

Look for concrete contradictions in:
- variable and argument roles
- control-flow order
- conditions and returns
- missing guards or assignments
- swapped names or arguments
- expected object or container shapes
- nearby caller and sibling conventions

Assume the repository was coherent before the injected mutation.

As soon as you can state a specific likely-wrong source statement and a
specific replacement supported by local evidence, your next tool call must
apply that repair.

Do not perform another search or read merely to increase confidence after a
specific supported repair is already identified.

If the correct repair is still ambiguous after the focused read, run the
smallest useful reproduction to distinguish the remaining alternatives.
A reproduction is a diagnostic tool, not a prerequisite to every edit.

If a focused read or reproduction has established the symptom and two further
diagnostic tool calls still have not produced an edit, apply the best locally
supported reversible repair and let verification judge it.

## Verification

After each production edit, immediately run the smallest focused check that
exercises the changed behavior.

Confirm that the check actually ran.

If the edit improves the target behavior and relevant kept tests still pass,
keep that repair even if another independent symptom remains.

If the latest edit causes a kept-test regression, narrow or revert only that
latest edit. Preserve earlier verified repairs.

If verification reveals another concrete defect connected to the task, locate
and repair that defect using the same loop.

Do not broaden into unrelated cleanup, refactoring, or speculative fixes.

Keep searches, reads, and command output small.
Do not dump whole files or large logs.

Before stopping, run the relevant kept tests and inspect the final diff.

Stop when the supported repairs are applied and checked.
Do not spend remaining calls collecting redundant confirmation.
