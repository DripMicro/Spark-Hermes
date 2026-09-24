# Fix the injected bug in /testbed

A small bug was injected into the Python project at `/testbed`. The tests that expose it were removed; the rest of
the test suite is still there. You earn credit for every removed test that passes after your change, and you score
zero if any test that passed before now fails.

## Facts about this machine — already checked, do not re-check them

- The project is at `/testbed`. There is no `/workspace`, `/repo` or `/app`.
- The interpreter that has the project's dependencies and pytest is `/opt/miniconda3/envs/testbed/bin/python`.
  The `python` on PATH has neither. Write the full path every time.
- Your tools are `terminal`, `read_file`, `search_files`, `patch` and `write_file`. You already have them. Do not call
  `tool_search` or `tool_call`, and do not open skills: everything you need is on this page.
- You get about 25 tool calls. Every tool output stays in the conversation and is paid for again on every later
  call, so one whole-file read early costs more than ten small ones.

## The plan — keep to the call numbers

1. **Calls 1–2: find the code.** `search_files` for the function, class or error message the issue names (content
   mode, limit 20). Do not list directories or browse the tree.
2. **Calls 3–4: see the bug.** Put the issue's example in `/tmp/repro.py` with `write_file` and run
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/repro.py 2>&1 | tail -20`. No example in the issue?
   Call the named function directly. The surviving tests in the matching test file show the expected values.
3. **Calls 5–6: read only the suspect function.** `read_file` with `offset` at the line `search_files` gave you and
   `limit` at most 80.
4. **Call 7 at the latest: patch.** Apply your best fix with `patch`, even if you are not sure. Episodes that never
   edit score zero, and that is how most episodes are lost. A wrong patch costs little: change it, or undo it with
   `git checkout -- <file>`.
5. **Calls 8–10: check.** Re-run the repro. Then run the test file for the module you changed:
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <test file> -q -x -p no:cacheprovider 2>&1 | tail -15`.
   A test that fails now but passed before means your patch is wrong: fix it or revert it.
6. **Then look for more.** Injected edits often come several to a file or module. If the issue describes more than
   one symptom, find and fix each site the same way.
7. **Finish.** Run `git diff`, undo anything you did not mean to change, and stop with a one-line reply.

## How to spot the injected edit

The edited line disagrees with what surrounds it: its docstring, its type hints, a sibling function that does the
same job, or its callers. Typical edits: a condition flipped (`<` for `<=`, `and` for `or`, a `not` added or
dropped), two arguments swapped, an off-by-one in a slice or `range`, a wrong constant or operator, a line, branch or
`return` removed, or a whole function rewritten into plausible but wrong code. Fix the line where the defect is, in
the smallest way that restores the documented behaviour. Do not refactor, reformat, or work around the bug elsewhere.

## Output discipline

- Never read a whole file: no `read_file` without `limit`, no `cat` of a source file.
- End any terminal command that can print more than a screen with `| head -40` or `| tail -30`.
- Never read the same lines twice. Never run the whole test suite.
- When you need two independent reads, ask for both in one response.

## Rules — breaking one scores zero

- Do not edit, add, move or delete tests or project configuration: nothing under `tests/`, no `conftest.py`,
  `pytest.ini`, `tox.ini`, `setup.cfg`, `setup.py` or `pyproject.toml`, no test data or golden files, and never a
  flag that rewrites expected output.
- No network and no installs: no `pip`, no `curl`, no `git fetch`.
- Write only inside `/testbed` (the fix) and `/tmp` (scratch).

## Where things are

| Project | Source | Tests | Watch out |
|---|---|---|---|
| cantools | `src/cantools/` | `tests/` | command-line tests compare exact stdout |
| python-docx | `src/docx/` | `tests/`, mirrors the source | warnings are errors; `features/` is not pytest |
| python-pptx | `src/pptx/` | `tests/`, mirrors the source | warnings are errors |
| astroid | `astroid/` | `tests/`, mostly flat | warnings are errors; an xfail test that passes fails |
| sqlglot | `sqlglot/` | `tests/` | `tests/fixtures/` holds golden files |
| pygments | `pygments/` | `tests/` | snapshot tests; never regenerate them |
| oauthlib | `oauthlib/` | `tests/`, mirrors the source | exact strings and error codes matter |
| marshmallow | `src/marshmallow/` | `tests/`, flat (`test_fields.py`, `test_schema.py`) | error messages are compared exactly; pytest adds `-v`, so pass `-q` |

Revision r0008.
