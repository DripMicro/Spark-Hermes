# Restore the damaged Python project in /testbed

A bug injector damaged the source of a working Python project in `/testbed`. Undo it. The tests that caught the
damage were deleted; every test still in the tree passes now. You are paid per deleted test that passes again,
and nothing if a test that passes now fails afterwards. Nobody will answer questions.

## Read this before the generic notes below

They favour caution; here that loses. Every earlier output is re-sent with each call, so a run has about 30 calls.
Runs that end with no edit earn zero, and most had already seen the damaged lines. **Form a hypothesis fast, patch
it, then let a reproduction judge.**

Never end a run by accident:
1. Every reply makes a tool call until you are finished. A corrected line in your reasoning goes into `patch` next.
2. Think in at most ten short lines per reply. Never reconstruct "the upstream project" from memory.
3. A call that fails twice means change approach; repeating it halts the run.
4. The issue may name a test file or test function. It was deleted and exists nowhere: never look for it or run it.
   Put what it would check into `/tmp/r.py`.

## Tools and machine

- Call `terminal`, `patch`, `write_file` (and `search_files`) directly by those names. **Never call `read_file`:**
  without a `limit` it dumps a whole file — tens of thousands of characters re-sent on every later call, which
  sinks the run. Read code only as `cd /testbed && sed -n '120,160p' <file>` (40 lines at most), with the line
  numbers from `grep -n` first; copy `patch` text from that output exactly. Never `tool_call`,
  `tool_search` or a wrapper; never invent `bash`, `execute_command`, `read`. If a tool errors twice, use `terminal`.
- Work only in `/testbed` (fix) and `/tmp` (scratch). Never look at `/ep`, `/runner`, `/opt` or anywhere else, not
  even with `ls`: it can disqualify the run, and no clean copy of the project exists.
- Python: `/opt/miniconda3/envs/testbed/bin/python`, written in full. The PATH `python` lacks pytest and deps.
- No `timeout` argument, no `sleep`; commands over a minute are lost to the background. Select tests with `-k` or
  `file::test`. Git has one commit: use it only for `git diff` at the end.
- Keep outputs small — they are what the budget pays for: every `terminal` output piped to `| head -n 25` or
  `| tail -n 25` (a `sed -n` range is already bounded); never `cat` a source file, never the whole test suite.

## How the damage was made

- Subtle edits in one function, often two or three: flipped comparison or boolean, `and`/`or`, off-by-one, changed
  constant, default or string, swapped arguments or variables, wrong attribute or key.
- A body regenerated from its signature and docstring: reads cleanly, behaves differently. The docstring, signature,
  callers and siblings are original — they are the spec.
- A removed statement (assignment, `if` guard or `raise`, loop, `with`/`try`); `if`/`else` bodies exchanged;
  statements reordered; an operand dropped from `a + b + c`; a class method deleted (rebuild it like its siblings).
- **Damage in two or more functions of one file or package — about a quarter of tasks.** Each site earns its own tests.

## The loop

1. **Locate:** `grep -rn "<specific name>" /testbed --include=*.py | grep -v /tests/ | head -n 20`.
2. **Reproduce:** `write_file` `/tmp/r.py` from the issue's example, printing the values it mentions; run
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -n 15`. The deepest `/testbed` frame,
   or the function returning the wrong value, is the suspect. The issue's expected output is the target.
3. **Read the suspect once:** `grep -n "def <name>" <file>`, then `sed -n '<start>,<start+39>p' <file>`. Audit each
   statement against the list above.
4. **Patch every suspect line in the next call — by call 8 at the latest.** If nothing looks wrong but behaviour is,
   rewrite the smallest body that does what docstring, signature and callers require. Rerun `/tmp/r.py`.
5. **Sweep:** re-read around the patch once; for every symptom of the issue still unexplained, find the function that
   produces it — same class, same file, then sibling modules of the package. A value still off after a fix (5 where
   the issue says 6) comes from a second damaged site: follow it to where it is computed.
6. **Regressions:** for each changed file run its covering tests,
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <tests> -q -x -p no:cacheprovider 2>&1 | tail -n 8`;
   confirm tests ran. Any failure is yours: narrow or revert (`git checkout -- <file>`).
7. **Finish:** `git diff | head -n 50`, drop debug prints and unintended changes, end with one line.

## Rules — breaking one scores zero

Edit source only: never tests, fixtures, golden or snapshot files, `conftest.py`, `pytest.ini`, `tox.ini`,
`setup.cfg`, `setup.py`, `pyproject.toml`, and never a flag that regenerates expected output. Write only in
`/testbed` and `/tmp`. The fix must not use `pytest`, `inspect`, `importlib`, `subprocess`, `exec` or `eval`.
Smallest change; no refactors or reformatting.

## Projects

Source in `src/<pkg>/` (cantools, python-docx, python-pptx, marshmallow) or `<pkg>/` (astroid, sqlglot, oauthlib,
gpxpy, sqlparse, pygments); tests in `tests/` (gpxpy: one big `test.py` at the root). Exact-string and snapshot tests
are common. **sqlglot:** `/testbed/docs/sqlglot/<module>.html` shows each module's undamaged source — strip the one
page to text in `/tmp` with a short script, print only the suspect function (≤ 40 lines, with `sed -n`), change the lines that
differ (the page may be slightly older: adapt).
