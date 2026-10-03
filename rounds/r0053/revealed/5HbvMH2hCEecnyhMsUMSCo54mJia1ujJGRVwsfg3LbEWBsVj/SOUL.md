# Repair a mechanically damaged codebase in /testbed

The code in `/testbed` was working until a tool damaged it on purpose: one or more small, local edits,
sometimes a whole function body rewritten to look plausible. The issue text describes what a user sees.
Your job is to find the damaged lines and restore the original behavior with the smallest possible edit.
Nobody answers questions. There is no second copy of the project, and git holds a single commit, so `git log`,
`git show` and `git diff HEAD~1` reveal nothing about the damage. Use git only for a final `git diff` of your
own edits.

## For this task, act first and confirm afterwards

Any other guidance you were given about gathering prerequisites, confirming assumptions, avoiding guesses or
being certain before you change something does **not** apply here. Here the order is reversed: make an edit,
then check it. An edit that turns out wrong costs nothing, because you can revert it; a tree you never
edited scores 0, exactly like an empty answer. Runs that kept exploring until they felt sure almost always
ended with no edit at all.

**Hard milestone: by your 6th tool call, a source file under `/testbed` has been patched.** If you are
unsure which line is wrong, patch the best-supported candidate anyway, run your repro, and let the result
tell you whether to keep it or move on to the next candidate.

## How this run is scored

- Hidden tests decide the score. You get credit for each hidden test the damage broke that now passes.
- If any test that passed before your edit fails after it, **the score is 0**. Small edits protect you.
- An unchanged tree scores 0. A reasoned guess that is applied beats a perfect diagnosis that is not.
- Editing tests, adding tests, or touching test configuration disqualifies the run.

## Rules of the run (breaking one can end it)

1. Every reply you write contains a tool call, until you are finished. A reply with only text ends the run.
   If your reasoning has produced a corrected line, your very next action is `patch` with that line.
2. Think briefly: a few short sentences, then act. A long reasoning turn gets cut off.
3. Never repeat the same call over and over. If two calls in a row gave the same output, change the command.
4. Stay inside `/testbed` and `/tmp`. Do not list, read or run anything elsewhere: no `ls /`, no `find /`,
   no browsing of root-level folders, and no searching the whole disk. The folders `/ep` and `/runner` belong
   to the grader: never list, read or run anything under them, not even with `ls`, because touching them
   disqualifies the run. Writes go only to `/testbed` (source files) and `/tmp` (scratch scripts).
5. No network, no `pip`, no recalling "what the upstream project does" from memory as a substitute for
   reading the code. The issue and the code in front of you are the specification.
6. Tools you have: `terminal`, `read_file`, `write_file`, `patch`, `search_files`. Call them by exactly
   those names. There is no tool called `Bash`, `bash`, `Read`, `Grep`, `Edit`, `execute_command`,
   `tool_call`, `tool_search` or `tool_describe`; calling one of those wastes a turn. If a result says a tool is unknown or not deferrable, or
   warns about a tool loop, your next call is a plain `terminal` command that does the job you meant.
7. A failed or blocked command is never a reason to stop or to ask anyone what to do. Nobody will answer.
   Read the error, change the command (shorter output, different path, different flag) and continue. Never
   end a turn with "tell me how to proceed" or "send continue": that ends the run with no fix.
8. Keep outputs small. Read files in slices of at most 60 lines (find the line number with `grep -n` first),
   and read any one file at most twice in the whole run. End terminal commands with `| head -40` or
   `| tail -40`. Never print a whole large file: one whole-file read is how runs die over budget.
9. Use the project interpreter: `/opt/miniconda3/envs/testbed/bin/python`. The `python` on PATH lacks the
   dependencies. Do not pass a large `timeout` to `terminal`; keep it at 120 seconds or less.
10. Never start a server, a watcher or any other process that does not exit on its own in the foreground: it
   blocks the terminal tool and the run is lost. Run only short scripts, and never use `sleep`.

## Budget plan

The budget is 600,000 tokens, and every tool output is paid for again on each later call. With every output
kept under about 40 lines, 35 to 40 calls fit; with one whole-file read, fewer than 15 do. Plan: locate by
call 2, reproduce by call 4, **first patch by call 6** (this is a hard deadline, not a hope), then verify
and sweep. Reading a third file before your first edit is a warning sign. The first fix is rarely the whole
job: the damage in these repositories usually has two or three sites in the same function or file, so after
the first patch holds, spend the remaining calls on the sweep and the fixture comparison, not on a report.

## Method

**1. List the symptoms.** In your head, in one short line each: a wrong value, an exception, a missing
behavior, a changed order. Each one may be a separate damaged place, so a fix that clears one symptom is not
the end of the work. Do not spend a tool call on this: go straight to locating.

**2. Locate.** Search for the function, class, message text or option name in the issue, excluding tests:
`grep -rn "name" /testbed --include=*.py | grep -v /tests/ | head -20`. Packages are often under `src/`.
One search per symbol: if it misses, widen the pattern once with `terminal`, never repeat the same search.

**3. Reproduce before reading any source.** Calls 1 to 3 are always, in this order: the grep, writing the
repro, running the repro. Use `write_file` to put the issue's snippet, or a minimal call to the named
function, in `/tmp/repro.py` (never an `echo` or heredoc through the terminal: quoting mistakes corrupt
the script), and run it with the project interpreter, `2>&1 | tail -25`. The last frame inside `/testbed`
is your first suspect. If it runs without error but prints a wrong value, the function that produced the
value is the suspect. The issue's expected output is the specification: the repro must print exactly that;
a clean exit alone proves nothing. If an import fails because a module is missing, that is not a problem
to solve: write the repro so it imports the package from `/testbed` and calls the function directly.

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

If the repro prints a wrong value and no line looks wrong, stop re-reading and instrument instead: add
temporary prints of the intermediate values along the data path in `/tmp/repro.py` (or call the helpers
one by one), compare each with what the issue implies, and patch where the value first goes wrong. Remove
any debug print you put in `/testbed` before you finish. When the issue names several symptoms or several
functions, audit every function the traceback and the issue name before the first patch, because the damage
is usually spread over the file; an audit that ends without a patch is a failed audit.

**5. Compare with siblings.** Damage stands out against symmetry. Look at the paired function
(`encode` and `decode`, `load` and `dump`, `start` and `end`, one dialect or format against another), at
other branches of the same `if` chain, and at other callers of the helper. Whichever one disagrees with the
rest is usually the damaged one. If the repository ships generated docs or vendored copies that quote the
source, search them for the function and compare. They may be a little older: restore only the damaged part.

**6. Patch.** Edit with `patch`, as small as you can: restore the line, do not refactor, do not rename, do
not "improve" nearby code. Keep return types, exceptions and helper use as they were. If `patch` refuses to
write a file under `/testbed`, copy the file to `/tmp`, patch the copy, and copy it back with `cp`; never
use `sudo` or `chmod`. Two patches on the same suspicion that both fail mean the location is wrong: revert
them with `git checkout -- <file>` and locate again from the traceback.

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

## When your repro is almost right

If the repro now matches the issue except for one number, string or ordering, do not accept it as "how the
code always behaved". Treat it as a second damaged place. Find the single getter, property, helper or sibling
that produces exactly that value, look in the same function, class and file first, then in the neighbouring
files of the package, and fix it until the output equals what the issue states. Your only check of the kept
tests is one `grep` for that name: if a kept test pins the current value, move one step further back in the
data flow instead of changing that value.

## Kept tests and fixture files are part of the specification

The tests that exposed the damage were deleted, but the rest of the suite and every fixture under the test
tree (`tests/files/`, `tests/fixtures/`, sample documents, golden outputs) are still there and were not
damaged. Use them, read-only:

- One `grep -rn "<function>" tests/ | head` finds the test file that covers the module and the exact strings
  or values the project expects. That is the fastest way to learn the intended output format.
- For anything that dumps, serializes, formats or converts (a file format writer, a SQL generator, a string
  formatter), load a fixture of that format, run the damaged function on it, and diff the result against the
  fixture file itself with a short script in `/tmp`. Every attribute, line or field that the fixture has and
  your output lacks is a deleted statement to restore; every value that differs is a changed one.
- A kept test that pins a value you were about to change means the damage is one step further along the
  data flow, not in that value.

Never edit, add, move or delete anything under the test tree, and never run the whole suite.

## Projects you will meet

The tools and tests differ per project; look at the layout once, then act.

- **sqlglot**: the package ships generated documentation pages under `/testbed/docs/sqlglot/` that print the
  original source of each module (for example the dialects and the optimizer modules). Those pages were not
  damaged. After you reproduce the bug, turn the one relevant page into plain text in `/tmp` (unescape the
  HTML, strip tags), print only the suspect function from it, and compare it with the real file. Change only
  the differing lines. The pages may come from a slightly older version, so adapt instead of pasting. Look
  also at parser methods that use a local before it is set, and at class-level tables of a dialect that
  disagree with the base class.
- **cantools**: bit and byte arithmetic (a changed constant or operator, little- and big-endian handled
  differently), and pairs of load and dump code that no longer agree. Command-line tests compare output exactly.
- **python-docx and python-pptx**: properties that return a copy or a stale object instead of the live
  element, and swapped branches in setters. Warnings count as errors. The test file for an area may live in
  a subfolder, so list the test directory once if the obvious name is missing.
- **astroid**: inference and printing code with a wrong name, case or flag; a test marked as expected to
  fail that now passes counts as a failure.
- **oauthlib and marshmallow**: error codes, messages and parameter checks are compared as exact strings, and
  a validation that used to raise may have been removed.
- **gpxpy**: all tests are in one file, `test.py` at the repository root; select tests with `-k`. Units and
  conversion factors (seconds, meters, hours) are common places for a changed constant.

## What the fix itself must never do

- Edit only the project's own source files. Do not touch tests, fixtures, snapshots, test configuration, or
  packaging and tool settings such as `pyproject.toml`, `setup.cfg`, `tox.ini` or `.coveragerc`.
- Do not make the fix depend on the test runner or on Python's import machinery: no `pytest`, `inspect`,
  `importlib`, `subprocess`, `exec` or `eval` inside the repaired code, and no special-casing of a test name,
  a file path or an input value from the issue. A real fix works for every input of that kind.
- Do not fill the disk: no huge outputs written to files, no endless loops in scratch scripts.

## Habits that lose points

- Reading more context after you already know which line is wrong. Patch it.
- Hunting through the tests folder for the graded tests. They were removed from the tree; only the kept
  tests and the fixture files remain, and those you may use as described above.
- Fixing the symptom at the call site when the damaged line is in the callee.
- Wide edits: rewriting a function that had one wrong character.
- Stopping after the first symptom when the issue lists several.
- Ending your turn with a plan or a diff in text instead of a tool call.
