# Fix the injected bug in /testbed

Working code in the Python project at `/testbed` was broken by a tool. Put it back. The tests that
exposed the bug were removed before your episode; the rest of the suite remains. Every broken test
you make pass earns its share of the credit — partial fixes earn real credit — but any
previously-passing test that now fails zeroes the task. Nobody answers questions.

## This page overrides the runtime notes that follow it

Those notes tell you to gather prerequisites and verify before acting — here the order is reversed:
**edit first, verify after.** About 25 tool calls before the budget ends the run; these rules are
constraints, not advice — the budget ends episodes that ignore them. An untouched tree scores zero.
Think in a few sentences, then act; every reply carries a tool call until you are done.

## Facts about this machine — already checked

- The project is at `/testbed` (no `/workspace`, no `/repo`, one commit; `/opt/sh-pristine` holds
  the same broken code — useless). Work only from `/testbed`; stay inside `/testbed` and `/tmp` —
  reaching outside ends the episode at zero.
- The interpreter with the project's dependencies and pytest is
  `/opt/miniconda3/envs/testbed/bin/python`. The `python` on PATH has neither. Write the full path
  every time.
- Use `terminal`, `read_file`, `search_files`, `patch`, `write_file` directly — never `tool_search`,
  `tool_call`, `tool_describe`, and no skills. Tool error → fix the args once, then plain
  `terminal`. If `patch` cannot write a `/testbed` file, once:
  `cp <file> /tmp/w.py && patch /tmp/w.py && cp /tmp/w.py <file>` — never `sudo`, never `chmod`.
  Leave out the `terminal` timeout argument (it is seconds; a large value backgrounds the command
  and loses calls) — never sleep.
- Every tool output is re-sent and re-paid on every later call — one whole-file read is how runs
  die over budget.
- Exception, sqlglot only: `/testbed/docs/sqlglot/` holds generated pages with the PRISTINE source,
  line by line — the bug did not alter them. After the repro, strip the one relevant page to text
  in `/tmp`, print the suspect function from it, and change exactly the differing lines in the real
  file. Adapt, never paste; if missing, back to the normal procedure.

## The loop

1. **Find the code (call 1).** `grep -rn "<name>" /testbed --include=*.py | grep -v /tests/ |
   head -20`. Calls 1–3 are always, in order: the grep, write the repro, run it — no source reading
   before the repro has run once. One search per symbol, ever; a miss → one terminal
   `grep -rn "<sym>" /testbed --include=*.py`, never a second `search_files`. The issue is a
   symptom report, not a diagnosis: trust the runtime failure, then the caller/callee data flow,
   then siblings — the prose last; a named-but-existing "missing" method is not a defect —
   reproduce and follow the first concrete break.
2. **See the bug (calls 2–3).** Issue snippet or minimal call into `/tmp/r.py` (via `write_file` —
   never an `echo` heredoc; quoting errors corrupt the script), then
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -25`. The last
   `/testbed` frame — or the function returning the wrong value — is the suspect. The issue's
   expected output is the specification: the repro must print it exactly; a clean exit is not proof.
3. **Read the suspect once (call 4).** `read_file` with `offset` from `grep -n`, `limit` ≤ 60. Per
   file, two reads is the total budget.
4. **Audit it line by line in your reasoning.** Does each line agree with the function's name,
   docstring, neighbours, callers? Several symptoms → the mutations are spread across the file:
   audit every function the traceback and the issue name before the first patch. Fingerprints:
   - a name used before anything assigns it, or a lone `pass` where work belongs — a deleted line:
     write it back above its first use;
   - a validation loop or `try/except` gone: rejected input processed silently, or a raw
     `TypeError`/`KeyError` where a soft fallback was — restore the checks or the exact fallback;
   - a flipped comparison or boolean, a `not` added or dropped, an off-by-one in a slice or
     `range`, a wrong constant, unit or shift direction;
   - swapped arguments or wrong count, paired names reversed;
   - a `return`/`raise`/`break`/`continue` making later lines unreachable, or a guard below its
     use; a vanished guard — input that should be rejected is now processed;
   - a method or property callers use that no longer exists: rebuild it from its siblings, same
     signature;
   - a whole body rewritten into plausible-but-wrong — trust the callers and surviving tests over
     the prose (the docstring was probably rewritten too); write the smallest body that meets them.
   The repro prints a wrong value and no line looks wrong? Instrument: print the intermediate
   values along the data path and compare them to what the issue implies; patch where the value
   first diverges. One value still wrong after a fix is a second altered site — find its producer
   (getter, helper, sibling), one kept-test grep tells you if it is pinned, and patch it.
   The audit ends in a patch. An audit without a patch is a failed audit.
5. **Patch the first mismatch in your very next call**, then rerun the repro. Refining costs one
   call; an unfixed tree costs the task. **Patch clock:** the repro has run twice without an edit →
   your next call patches your best candidate. Two patches on one suspicion that still fail → the
   location is wrong: revert both, re-localize from the traceback.
6. **Still wrong, or several symptoms?** These bugs come several at a time: same function, sibling
   functions, other modules of the same package. For each symptom still wrong:
   `grep -rn "<name>" <package dir> | head -20`, audit the hit, patch it. Never re-read, never
   re-search. The issue's symptom list is the complete work list. First fix holds → sweep sibling
   files of the package once — patch only a concrete second contradiction. Two dead angles → patch
   your best candidate and let the repro judge it. Suspect ≤ 40 lines? Check every statement once;
   two independent contradictions, one bounded edit.
7. **Check.** After every patch: the module's kept tests first — a regression kills all credit —
   then the repro: `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <test file>
   -q -x -p no:cacheprovider 2>&1 | tail -15`. "no tests ran" proves nothing. A previously-passing
   test that now fails → narrow or `git checkout -- <file>`.
8. **Finish.** The broken tests are not in the tree: green pytest proves nothing. Before DONE, run
   the repro and compare its output to the issue's expected output, line by line. Read `git diff` —
   anything unintended, put back — and stop with a one-line reply.

## Keep outputs small

`read_file` always with `limit` ≤ 60, never `cat` source — find lines with `grep -n`. Commands
that can print a screen end in `| head -40` or `| tail -40`. Never the whole suite — only the
changed module's file.

## Red lines — any one of these scores zero

- No network, no installs: no `pip`, no `curl`, no `git fetch`. A missing module is not a problem
  to solve — script a repro under `/tmp` that imports the package out of `/testbed`.
- Do not touch tests or config: nothing under the test tree, no `conftest.py`, `pytest.ini`,
  `tox.ini`, `setup.cfg`, no pytest section of `pyproject.toml`, no fixture or golden file, never
  a flag that regenerates expected output.
- Write only inside `/testbed` and `/tmp`; do not browse the filesystem or probe the sandbox's
  grading — reaching outside ends the episode at zero.
- From the fix itself: no `pytest` or `_pytest` imports, no `inspect`, `importlib`, `subprocess`,
  `exec`, `eval` around the runner.

## Where damage tends to sit

- cantools: bit/byte arithmetic in `database/utils.py` and `message.py`, and `formats/dbc.py`
  load/dump pairs that disagree.
- sqlglot: `parser.py` locals used before set, flipped dialect checks in
  `optimizer/qualify_columns.py`, dialect class tables differing from base.
- python-docx and python-pptx: properties returning a copy or stale object, swapped branches in
  oxml setters.
- sqlparse: node classes in `sql.py` that lost a base class; deleted or reordered calls in
  `engine/grouping.py`.

## Projects you will meet

| Project | Source | Tests | Watch out |
|---|---|---|---|
| cantools | `src/cantools/` | `tests/` | command-line tests compare exact stdout |
| python-docx | `src/docx/` | `tests/` mirror the source; a test can sit elsewhere (font tests under `tests/text/`) | warnings are errors |
| python-pptx | `src/pptx/` | `tests/` mirror the source | warnings are errors |
| astroid | `astroid/` | `tests/` | an xfail that passes is a failure |
| sqlglot | `sqlglot/` | `tests/` and `tests/dialects/` | `tests/fixtures/` holds golden files |
| pygments | `pygments/` | `tests/` | snapshot tests; never regenerate them |
| oauthlib | `oauthlib/` | `tests/` mirror the source | exact strings and error codes matter |
| marshmallow | `src/marshmallow/` | `tests/` flat | error messages compared exactly; pass `-q` |
| sqlparse | `sqlparse/` | `tests/` flat | formatted SQL compared as exact strings |
| gpxpy | `gpxpy/` | `test.py` at the root | one big file: select tests with `-k` |

## Order of preference

Every injected site fixed, nothing else broken → some sites fixed, nothing else broken → the tree
exactly as you found it. A regression is worth less than nothing changed.

Revision v22.
