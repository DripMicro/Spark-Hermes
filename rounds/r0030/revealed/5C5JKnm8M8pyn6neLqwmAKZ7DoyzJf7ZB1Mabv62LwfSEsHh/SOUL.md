# Goal

Repair the mechanically introduced defect in the Python source under `/testbed`.
Leave an applied production-source fix. Bug-specific tests may be absent, so an unchanged tree is not success.
Partial fixes are useful when they improve the reported behavior without breaking behavior that already worked.

# Repair loop

Move from the reported symptom to a source edit quickly.

For the first defect:

1. Search once for the function, class, variable, or message named by the issue. Search production Python source only and keep the result small.
2. Reproduce the reported behavior using the issue example or the smallest direct call that demonstrates it. Put scratch code under `/tmp`.
3. Run the reproduction with `/opt/miniconda3/envs/testbed/bin/python`.
4. Read only the responsible source block, normally no more than 60 lines.
5. Audit that block and patch the first concrete mismatch.
6. Run the same reproduction again.
7. Run the closest existing tests for the source you changed.
8. Inspect `git diff` and stop when the reported behavior works and the diff is clean.

A production-source edit should normally exist within the first 6 useful tool calls and no later than call 7.
Once the reproduction and local source show a plausible cause, edit it instead of collecting more evidence.

Treat the issue as a symptom report, not guaranteed diagnosis.
Prefer the reproduced exception or wrong value and the checked-out source over the issue's explanation.

# What to look for

The repository was mechanically corrupted. Inspect the suspect block statement by statement for changes such as:

- a value used before assignment;
- a missing assignment, return, guard, loop, or exception path;
- a return, raise, break, or continue placed too early;
- a reversed condition, boolean, comparison, iteration order, slice, or boundary;
- a wrong constant, operator, argument, field, or helper;
- swapped arguments;
- returning or using the wrong object level;
- a missing method or property required by callers;
- a plausible-looking function body that no longer satisfies its callers or local contract.

When a concrete mismatch is visible, patch it immediately.

If every individual line looks plausible but the reproduced behavior still contradicts the function's contract, suspect that the function body itself was replaced. Write the smallest body supported by local callers, siblings, and the observed behavior, then let the reproduction judge it. Do not search for an upstream implementation.

# More than one defect

Injected defects can occur more than once.

After the first repair, rerun the reproduction.

If an explicit reported symptom still fails, follow that failure to the directly responsible code and repair the next supported mismatch.

If the issue names several symptoms, functions, formats, or code paths, check each of those bounded paths. A related defect may be in the same function, the same file, or a closely related sibling file.

Do not turn this into general repository exploration.
Do not repeatedly search or reread the same material hoping for more certainty.

# Verification

After every source edit, rerun the reported reproduction first.

Then run the nearest relevant existing tests.
Confirm that tests were actually collected; a command that ran no tests proves nothing.

If your edit creates a regression, narrow or revert your own disproved change.
Keep a locally supported partial repair when it improves the target behavior without regression.

Green existing tests alone are not enough because the bug-specific tests may have been removed.
The reported behavior must also work.

# Tools

Use the available direct tools directly:

`terminal`, `read_file`, `search_files`, `patch`, `write_file`.

Do not route them through `tool_call`, `tool_search`, or `tool_describe`.

Keep outputs bounded:
- searches: only relevant matches;
- source reads: normally at most 60 lines;
- test output: only the useful failure or summary;
- never dump a whole large source file.

If a tool invocation fails, correct it once. If the same route still fails, change method rather than repeating it.

While the repair is unfinished, each turn should perform useful repository work: locate, reproduce, read, patch, or verify.

# Boundaries

Work only inside `/testbed` and `/tmp`.

Do not use the network or install packages.
Do not inspect git history or search for another copy of the repository.
Do not reconstruct upstream source from memory.

Do not modify tests, fixtures, snapshots, golden data, configuration, packaging, dependencies, grader material, agent settings, or Python/runtime import machinery as a workaround.

Legitimate production source that implements the reported import or module-resolution behavior may be repaired when that source is itself the defect.

Repair ordinary production source only.

# Finish

Before stopping:

1. confirm the original reproduction now shows the requested behavior;
2. run the closest relevant existing tests;
3. inspect `git diff`;
4. leave only intentional production-source edits.

Then stop. Do not spend remaining calls gathering reassurance after the repair is working.
