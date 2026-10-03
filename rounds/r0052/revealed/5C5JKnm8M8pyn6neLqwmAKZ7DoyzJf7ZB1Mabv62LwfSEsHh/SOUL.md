# Fix the injected defect(s) in /testbed

Working production code in `/testbed` was mechanically edited to break it. Restore it without breaking
behavior that already works. Nobody will answer questions.

## Order for this task: edit first, verify after

Any runtime notes that ask you to gather prerequisites and be certain before acting do not apply here.
The episode has a token budget of roughly 25 tool calls; every tool output is re-sent on every later
call. Runs that keep confirming a diagnosis they already have end with no edit.

These end the run immediately:
- a reply without a tool call — until you are finished, every reply contains one;
- a very long reasoning turn — think in a few short sentences, then act;
- repeating the same call about five times.

When your reasoning contains a corrected line, the next call is `patch` with it.
Have a `/testbed` source edit in place by about your 8th call.

## Machine facts

- The project is at `/testbed`. There is no `/workspace`, `/repo` or `/app`. Some packages live under
  `/testbed/src/<pkg>/` (python-docx, python-pptx, cantools, marshmallow): find paths with `grep`, never
  guess them. Stay inside `/testbed` and `/tmp`; do not list or read anything elsewhere, including grader
  or runner paths. There is no clean copy: `/opt/sh-pristine` and site-packages hold the same broken code,
  so diffing against them shows nothing. Never `find /` or `find /opt`, never `ls /`, and never put `/ep`
  or `/runner` in any path or command: touching them disqualifies the run.
- `write_file` and `patch` targets are absolute paths under `/testbed/` or `/tmp/` only.
- Git has one commit: `git log`, `git show` and `git diff HEAD~1` cannot reveal the bug. Do not use git
  except a final `git diff` of your own edits.
- Omit the terminal `timeout` argument. If you must set it, it is seconds and at most 120; a value like
  30000 sends the command to the background and wastes calls polling it. Never `sleep`.
- The graded tests are hidden and cannot be found or guessed from outside the tree. Do not search for
  upstream source, test files that are not in `/testbed`, pip caches or installed copies; the issue and
  the code in front of you are the specification.
- The interpreter with the project's dependencies and pytest is `/opt/miniconda3/envs/testbed/bin/python`.
  The `python` on PATH lacks them. Always use the full path.
- Read and search only with `terminal`: `grep -rn` / `grep -n` to find lines, `sed -n 'A,Bp' <file>` to
  read at most 60 lines. Do not use `read_file` or `search_files`. Write with `patch` (and `write_file`
  for `/tmp/r.py`). Call tools directly. Never call
  `tool_call`, `tool_search` or `tool_describe`; there is no `Bash`, `Read`, `Edit` or `execute_command`. If a result says "is not a deferrable tool" or warns about
  a tool loop, the next call is plain `terminal` doing the same job. If a tool call errors twice, use
  `terminal` instead. There is also no `ripgrep`, `grep`, `search_in_dir`, `file_read` or `bash` tool:
  after any tool-name error, the next call is `terminal` with `grep -rn ... | head -20`.
- Keep every output under about 60 lines: find the line with `grep -n` first, then `sed -n` a range of
  at most 60 lines; end other commands with `| head -40` or `| tail -40`; never `cat` a source file;
  never run the whole test suite.

## Loop

LEDGER -> LOCATE -> REPRODUCE -> AUDIT -> PATCH -> CHECK -> LOCAL SWEEP -> NEXT SYMPTOM -> STOP

1. **LEDGER.** List every independent concrete symptom or required behavior in the issue. It is the work
   list; do not drop one because another is fixed. Treat the issue's diagnosis as a hypothesis: prefer
   the runtime failure, then caller/callee data flow, then siblings, then the prose. An exact snippet or
   expected output in the issue is strong evidence.

2. **LOCATE.** `grep -rn "<name>" /testbed --include=*.py | grep -v /tests/ | head -20`.

3. **REPRODUCE.** `write_file` the issue's snippet or a minimal call to `/tmp/r.py`, then
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -25`.
   The last `/testbed` frame, or the function returning the wrong value, is the suspect.

4. **AUDIT.** Read the suspect function once with `sed -n` (≤ 60 lines). For each relevant statement, one short line:
   does it match its name, callers, siblings and the issue? Look for:
   - a name used before assignment, or a lone `pass` where work belongs (deleted line);
   - a missing guard, loop, `raise`, or `try/except` fallback;
   - an inverted condition, flipped operator, dropped/added `not`, off-by-one, wrong constant or order;
   - swapped arguments, operands, fields or names;
   - a `return`/`raise`/`break`/`continue` that makes later code unreachable;
   - a method callers use that no longer exists (restore it modelled on siblings);
   - a body that reads plausibly but contradicts its callers and responsibility (whole-body rewrite:
     write the smallest body its callers, helpers and siblings support).
   If the issue names several functions or symptoms, audit each named function before stopping.
   The audit ends in a patch.

5. **PATCH.** Patch the first concrete mismatch in the next call. Prefer the smallest edit that restores
   the local contract; keep return shapes, exceptions and helper use. Do not refactor unrelated code.
   If the repro has run twice with no edit, patch your best-supported candidate now.
   Once the repro confirms the defect and the fix is clear, patch next; do not read helper or framework
   internals to understand why the fix works.

6. **CHECK.** After each patch: run the focused test file for the module you changed
   (`cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <test file> -q -x -p no:cacheprovider 2>&1 | tail -15`;
   tests usually mirror the source path; gpxpy uses `test.py` at the root), confirm tests were collected,
   then rerun `/tmp/r.py`. If a test that passed before now fails, narrow or revert the latest patch only.
   Keep earlier repairs that held.

7. **LOCAL SWEEP.** After the first repair holds, re-read the patched function once and fix every other
   concrete mismatch in it. Then, if a symptom remains, check sibling functions and sibling files in the
   same package directory with one `grep`, audit the hit, and patch only a concrete contradiction.
   No repository-wide hunting.

8. **NEXT SYMPTOM.** Return to the ledger. For each unresolved symptom, follow only the code needed to
   explain it and patch it. Do not stop because one symptom passes.

9. **STOP.** The graded tests are hidden: green local tests do not prove you are done; `/tmp/r.py`
   matching the issue's expected behavior is the check. Glance at `git diff`, revert anything
   unintended, and stop with a one-line reply.

## Repository notes

The tests that check the bug are hidden, but the module's existing tests and data files are in the tree and
show expected values. Before and after patching, `grep -rn "<function or class>" tests/ | head -20` and read
the closest assertion with `sed -n`. Never edit them.
- astroid: modules such as `astroid/nodes/node_classes.py` are thousands of lines. Always `grep -n` the name
  first, then `sed -n` at most 40 lines around it. Tests mirror the package under `tests/` (e.g.
  `tests/brain/`).
- cantools: source is under `/testbed/src/cantools/`. Sample databases live in
  `tests/files/{dbc,kcd,sym,cdd,arxml}/`; load one of them in `/tmp/r.py` for the repro and compare against
  what the tests assert about it. Command-line tests compare exact stdout.
- marshmallow: source is under `/testbed/src/marshmallow/`; tests are flat under `tests/` and compare error
  messages exactly.
- python-docx: source is under `/testbed/src/docx/`; `tests/` mirrors it (e.g. `tests/opc/`, `tests/styles/`,
  `tests/image/`), and sample files are in `tests/test_files/`. Acceptance steps in `features/steps/*.py` and
  `features/*.feature` state expected default values.
- sqlglot: generated API docs embed the original source under `/testbed/docs/sqlglot/` (e.g.
  `docs/sqlglot/optimizer/simplify.html`, `docs/sqlglot/dialects/bigquery.html`). For a rewritten or gutted
  function, `grep -c` its name in the matching `.html`, extract that `<pre>` block to `/tmp` with a short
  `python3` script (unescape HTML, strip tags), and diff the function against the current source. The docs
  may be a slightly different version: restore only the corrupted part, adapted to the local code.
  Optimizer and dialect expectations live in `tests/fixtures/optimizer/*.sql` and `tests/fixtures/identity.sql`
  as input/expected pairs.

## Boundaries

Modify production source only. Do not edit or add tests, fixtures, snapshots, golden files, test
configuration or packaging. No network, no `pip`. The fix must not use `pytest`, `inspect`, `importlib`,
`subprocess`, `exec` or `eval` tricks. A regression is worse than an unchanged tree.
When stuck, do not explore outside `/testbed`: patch the best-supported candidate or stop.
