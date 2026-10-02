# Repair a mechanically damaged codebase in /testbed

The code in `/testbed` was working until a tool damaged it on purpose: one or more small, local edits,
sometimes a whole function body rewritten to look plausible. The issue text describes what a user sees.
Your job is to find the damaged lines and restore the original behavior with the smallest possible edit.
Nobody answers questions. There is no second copy of the project and no history to compare with.

## How this run is scored

- Hidden tests decide the score. You get credit for each hidden test the damage broke that now passes.
- If any test that passed before your edit fails after it, **the score is 0**. Small edits protect you.
- An unchanged tree scores 0. A reasoned guess that is applied beats a perfect diagnosis that is not.
- Editing tests, adding tests, or touching test configuration disqualifies the run.

## Rules of the run (breaking one can end it)

1. Every reply you write contains a tool call, until you are finished. A reply with only text ends the run.
   If your reasoning has produced a corrected line, your very next action is `patch` with that line.
2. Think briefly: a few short sentences, then act. A long silent reasoning turn gets cut off.
3. Never repeat the same call over and over. If two calls in a row gave the same output, change the command.
4. Stay inside `/testbed` and `/tmp`. Do not list, read or run anything elsewhere: no `ls /`, no `find /`,
   no browsing of root-level folders, and no searching the whole disk. Reading paths that belong to the
   grader or runner disqualifies the run. Writes go only to `/testbed` (source files) and `/tmp` (scratch scripts).
5. No network, no `pip`, no recalling "what the upstream project does" from memory as a substitute for
   reading the code. The issue and the code in front of you are the specification.
6. Tools you have: `terminal`, `read_file`, `write_file`, `patch`, `search_files`. Call them by those names.
   If a result says a tool is unknown or not deferrable, or warns about a tool loop, your next call is a
   plain `terminal` command that does the job you meant.
7. Keep outputs small. Read files in slices of at most 60 lines (find the line number with `grep -n` first).
   End terminal commands with `| head -40` or `| tail -40`. Never print a whole large file.
8. Use the project interpreter: `/opt/miniconda3/envs/testbed/bin/python`. The `python` on PATH lacks the
   dependencies. Do not pass a large `timeout` to `terminal`; keep it at 120 seconds or less.

## Budget plan

You have roughly 25 useful tool calls before cost becomes a problem, and every output is paid for again on
each later call. Aim for: locate by call 2, reproduce by call 4, first patch by call 6, verify and sweep after.

## Method

**1. List the symptoms.** Before touching anything, write one line per concrete complaint in the issue:
a wrong value, an exception, a missing behavior, a changed order. Each one may be a separate damaged place.
A fix that clears one symptom is not the end of the work.

**2. Locate.** Search for the function, class, message text or option name in the issue, excluding tests:
`grep -rn "name" /testbed --include=*.py | grep -v /tests/ | head -20`. Packages are often under `src/`.

**3. Reproduce.** Use `write_file` to put the issue's snippet, or a minimal call to the named function, in
`/tmp/repro.py`, and run it with the project interpreter, `2>&1 | tail -25`. The last frame inside
`/testbed` is your first suspect. If it runs without error but prints a wrong value, the function that
produced the value is the suspect.

**4. Audit the suspect, line by line.** Read it once. For every line decide: does it agree with the name of
the function, its docstring, its callers, the neighbouring functions, and the issue? Write the verdict as a
few words per line, only for lines that look odd. Typical damage:

- a name that is read before it is assigned, or an assignment replaced by `pass`: the statements were
  shuffled or one was deleted; put the assignment back before its first use
- a check that vanished: a guard on empty or `None`, a validation that used to raise, a loop that used to
  handle every item, a fallback in `except`
- a changed operator, comparison, `and`/`or`, a missing or extra `not`, an off-by-one, a changed numeric
  constant or unit factor, swapped operands or swapped arguments, `<` for `<=`, `//` for `/`
- a return or raise that sits too early, so later code cannot run; a loop that exits after one pass
- a string, key, flag or format that differs slightly from its siblings (case, separator, prefix)
- a method or helper that callers use but that is gone or returns a fixed value
- a body that reads smoothly yet does not do what its name and callers need: rewrite it as the smallest
  body that satisfies its callers, reusing the helpers its siblings use

**5. Compare with siblings.** Damage stands out against symmetry. Look at the paired function
(`encode` and `decode`, `load` and `dump`, `start` and `end`, one dialect or format against another), at
other branches of the same `if` chain, and at other callers of the helper. Whichever one disagrees with the
rest is usually the damaged one. If the repository ships generated docs or vendored copies that quote the
source, search them for the function and compare. They may be a little older: restore only the damaged part.

**6. Patch.** Edit with `patch`, as small as you can: restore the line, do not refactor, do not rename, do
not "improve" nearby code. Keep return types, exceptions and helper use as they were.

**7. Check.** Rerun `/tmp/repro.py`. Then run the test file that mirrors the changed module:
`cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest path/to/test_file.py -q -x -p no:cacheprovider 2>&1 | tail -15`
(tests usually mirror the source path; some projects keep one test file in the root). Confirm tests were
collected. If something that used to pass now fails, your last patch is too wide: narrow or revert it, and
keep earlier patches that held. Never run the whole suite.

**8. Sweep.** The first fix often hides a second. Re-read the patched function once and fix every other
line that disagrees with its purpose. If the repro still differs from what the issue expects, check the
sibling functions in the same file, then the neighbouring files in the same package directory, with one
`grep` each. Patch only a concrete contradiction. Do not wander the whole repository.

**9. Stop.** Local tests passing is not proof, because the real tests are hidden. The proof is that your
repro now shows exactly what the issue says it should. Look at `git diff` once, undo anything you did not
mean to change, and end with one short line.

## What the fix itself must never do

- Edit only the project's own source files. Do not touch tests, fixtures, snapshots, test configuration, or
  packaging and tool settings such as `pyproject.toml`, `setup.cfg`, `tox.ini` or `.coveragerc`.
- Do not make the fix depend on the test runner or on Python's import machinery: no `pytest`, `inspect`,
  `importlib`, `subprocess`, `exec` or `eval` inside the repaired code, and no special-casing of a test name,
  a file path or an input value from the issue. A real fix works for every input of that kind.
- Do not fill the disk: no huge outputs written to files, no endless loops in scratch scripts.

## Habits that lose points

- Reading more context after you already know which line is wrong. Patch it.
- Reading the tests folder to learn expected behavior. The graded tests are not there, and the code plus the
  issue are enough.
- Fixing the symptom at the call site when the damaged line is in the callee.
- Wide edits: rewriting a function that had one wrong character.
- Stopping after the first symptom when the issue lists several.
- Ending your turn with a plan or a diff in text instead of a tool call.
