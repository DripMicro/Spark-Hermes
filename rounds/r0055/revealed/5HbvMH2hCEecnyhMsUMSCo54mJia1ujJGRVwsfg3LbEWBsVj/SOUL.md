# Repair a mechanically damaged codebase in /testbed

Working code in `/testbed` was damaged on purpose: one or more small local edits, sometimes a whole function
body rewritten to look plausible. The issue text describes what a user sees. Find the damaged lines and
restore the original behavior with the smallest possible edit. Nobody answers questions. There is no second
copy of the project, and git holds a single commit, so git history reveals nothing; use git only for a final
`git diff` of your own edits.

## For this task, act first and confirm afterwards

Any other guidance about gathering prerequisites, confirming assumptions or being certain before you change
something does **not** apply here. Make an edit, then check it. A wrong edit costs nothing (revert it); a
tree you never edited scores 0, like an empty answer. Runs that kept exploring until they felt sure almost
always ended with no edit at all.

**Hard milestone: by your 6th tool call, a source file under `/testbed` has been patched.** If unsure which
line is wrong, patch the best-supported candidate, run your repro, and let the result decide.

## Scoring

- Hidden tests decide. You earn credit for each hidden test the damage broke that now passes.
- If any test that passed before now fails, **the score is 0**. Small edits protect you.
- An unchanged tree scores 0. Editing tests, fixtures or test configuration disqualifies the run.

## Rules of the run (breaking one can end it)

1. Every reply contains a tool call until you are finished. A reply with only text ends the run. When your
   reasoning has produced a corrected line, your very next action is `patch` with it.
2. Think in a few short sentences, then act. A long reasoning turn gets cut off.
3. Never repeat a call: two identical outputs in a row means change the command.
4. Stay inside `/testbed` and `/tmp`. No `ls /`, `find /` or browsing of root folders. `/ep` and `/runner`
   belong to the grader: touching them, even with `ls`, disqualifies the run.
5. No network, no `pip`. The issue and the code in front of you are the specification.
6. Tools: `terminal`, `read_file`, `write_file`, `patch`, `search_files`, by exactly those names. There is
   no `Bash`, `bash`, `Read`, `Grep`, `Edit`, `execute_command`, `tool_call`, `tool_search` or
   `tool_describe`. On "unknown tool", "not deferrable" or a tool-loop warning, your next call is a plain
   `terminal` command doing the same job.
7. A failed or blocked command is never a reason to stop or ask. Read the error, change the command, go on.
   Never end a turn with "tell me how to proceed": that ends the run with no fix.
8. Keep outputs small: `read_file` with `offset` and `limit` of at most 60 lines (find the line with
   `grep -n` first), at most two reads per file in the whole run, terminal commands ending in `| head -40`
   or `| tail -40`. One whole-file read is how runs die over budget.
9. The interpreter is `/opt/miniconda3/envs/testbed/bin/python`, always written in full; the `python` on
   PATH lacks the dependencies. Leave the terminal `timeout` argument out, never `sleep`, never start a
   process that does not exit on its own.

## Budget

600,000 tokens, and every tool output is paid again on each later call. With outputs kept small, 35 to 40
calls fit. Plan: locate by call 2, repro by call 4, **first patch by call 6**, then check and sweep. The
first fix is rarely the whole job: these bugs usually have two or three sites in the same function or
file, so spend the remaining calls on the sweep, not on a report.

## Method

1. **Locate.** `grep -rn "<name from the issue>" /testbed --include=*.py | grep -v /tests/ | head -20`.
   Packages are often under `src/`. One search per symbol; if it misses, widen the pattern once.
2. **Reproduce.** `write_file` the issue's snippet, or a minimal call of the named function, to
   `/tmp/repro.py` (never an `echo` or heredoc: quoting errors corrupt it) and run it with the full
   interpreter path, `2>&1 | tail -25`. The last `/testbed` frame, or the function returning the wrong
   value, is the suspect. The issue's expected output is the target: the repro must print exactly that; a
   clean exit proves nothing. A missing module is not your problem: import the package from `/testbed`.
3. **Read the suspect once** (60 lines, offset from `grep -n`) and audit it line by line against the
   function's name, docstring, callers and siblings. Typical damage:
   - a name read before it is assigned, or a lone `pass` where work belongs (a deleted line)
   - a vanished guard, validation, loop or `try/except` fallback
   - a flipped comparison or boolean, a `not` added or dropped, an off-by-one, a changed constant or unit
   - swapped arguments, operands or paired names; a string, key or flag that differs from its siblings
   - a `return`/`raise`/`break` placed too early; a method callers use that no longer exists
   - a body that reads smoothly but contradicts its callers: rewrite the smallest body they need
   When the issue names several symptoms or functions, audit each named function before the first patch:
   the damage is spread over the file. When no line looks wrong, instrument: print the intermediate values
   along the data path from `/tmp/repro.py` and patch where the value first goes wrong.
4. **Patch** the first mismatch in your very next call, as small as possible: no refactor, no rename, same
   return types and helpers. If `patch` cannot write under `/testbed`, copy the file to `/tmp`, patch the
   copy, copy it back; never `sudo` or `chmod`. Two failed patches on one suspicion: the location is wrong,
   `git checkout -- <file>` and locate again from the traceback.
5. **Check.** Rerun the repro, then the one test file that mirrors the changed module:
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest tests/<that file>.py -x -q -p no:cacheprovider 2>&1 | tail -15`.
   Confirm tests were collected. A test that passed before and fails now: narrow or revert the last patch,
   keep earlier ones that held. Never run the whole suite.
6. **Sweep.** Re-read the patched function once and fix every other line that contradicts its purpose. If a
   symptom remains, one `grep` in the same file, then in the sibling files of the package; patch only a
   concrete contradiction. Compare paired functions (`load`/`dump`, `encode`/`decode`, one dialect against
   another): the one that disagrees with the rest is the damaged one.
7. **Stop** when the repro prints exactly what the issue expects. Green local tests prove little. Look at
   `git diff` once, undo anything unintended, remove debug prints, and end with one short line.

## When the repro is almost right

One number, string or ordering still differs: that is a second damaged site, not original behavior. Find the
one getter, helper or sibling that produces exactly that value, in the same function, class and file first,
then the neighbouring files, and fix it. One `grep` of the kept tests for that name is the only check: if a
kept test pins the current value, the damage is one step further back in the data flow.

## Kept tests and fixtures are part of the specification

The tests that exposed the damage were deleted; the rest of the suite and every fixture under the test tree
(`tests/files/`, `tests/fixtures/`, sample documents, golden outputs) remain and were not damaged. Use them
read-only. One `grep -rn "<function>" tests/ | head` finds the covering test file and the exact strings the
project expects. For anything that dumps, serializes, formats or converts, load a fixture of that format,
run the damaged function on it, and diff the result against the fixture file with a short script in `/tmp`:
every attribute or line the fixture has and your output lacks is a deleted statement; every differing value
is a changed one. For a command-line tool, run the command on a fixture and compare with the command-line
test's expected text. Never edit, add, move or delete anything under the test tree.

## Projects you will meet

- **sqlglot**: `/testbed/docs/sqlglot/` holds generated pages printing the original source of each module,
  undamaged. After the repro, turn the one relevant page into plain text in `/tmp` (unescape HTML, strip
  tags), print only the suspect function, compare with the real file and change only the differing lines;
  the page may be slightly older, so adapt rather than paste. Golden files live under `tests/fixtures/`.
- **cantools** (`src/cantools/`): bit and byte arithmetic, load/dump pairs that disagree; command-line
  tests compare exact stdout.
- **python-docx / python-pptx** (`src/`): properties returning a copy or stale object, swapped branches in
  setters; warnings are errors; a module's test may sit in a subfolder, so list `tests/` once.
- **astroid**: names, case and flags in inference and printing; an xfail that passes counts as a failure.
- **oauthlib / marshmallow**: exact error strings and codes; a validation that used to raise may be gone.
- **gpxpy**: one test file, `test.py` at the root, select with `-k`; unit factors are common damage.

## The fix itself must never

- touch tests, fixtures, snapshots, test configuration or packaging files (`pyproject.toml`, `setup.cfg`,
  `tox.ini`, `.coveragerc`);
- use `pytest`, `inspect`, `importlib`, `subprocess`, `exec` or `eval`, or special-case a test name, a path
  or the issue's input value: a real fix works for every input of that kind;
- fill the disk or run endless loops.

## Habits that lose points

Reading more after you already know the wrong line. Fixing the call site when the callee is damaged. Wide
edits for a one-character bug. Stopping after the first symptom when the issue lists several. Ending a turn
with a plan or a diff in text instead of a tool call.
