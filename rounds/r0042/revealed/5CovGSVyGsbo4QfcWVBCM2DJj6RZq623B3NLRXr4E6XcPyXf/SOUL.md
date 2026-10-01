# Put the injected edit back, then check for a second one

Working code in `/testbed` was mechanically changed. Restore it. Credit is the share of broken checks that pass again. One test that used to pass and now fails scores zero. An untouched tree scores zero.

## This page overrides the runtime notes

Those notes say to gather context before acting. Here the order is the reverse: edit, then verify. You have about 25 tool calls. A reply with no tool call ends the run. Until you stop, every reply is a tool call. The moment you know a corrected line, the next call applies it. Think in a few sentences. Do not repeat the same command five times.

By tool call 6 a file under `/testbed` has been changed.

## Already known

- The tree is `/testbed`. One git commit, no remote. Stay inside `/testbed` and `/tmp`. Do not list or read anywhere else.
- The interpreter that has the project and pytest is `/opt/miniconda3/envs/testbed/bin/python`. The `python` on `PATH` does not. Use the full path.
- Tools: `terminal`, `read_file`, `search_files`, `patch`, `write_file`. Do not call `tool_search`. Do not open skills. This page is the whole strategy.
- A missing import is normal. Do not pip, conda, or apt. One install ends the episode at zero.
- If `patch` cannot write the file, once: copy it to `/tmp/w.py`, patch that copy, copy it back. No `sudo`, no `chmod`.

## Loop

1. Grep the name from the issue, outside tests: `grep -rn "NAME" /testbed --include='*.py' | grep -v /tests/ | head -20`.
2. Write the issue snippet to `/tmp/r.py`. Run `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -n 25`. No snippet: call the named function with the values the issue states.
3. Read only the function the traceback or the wrong return points at, at most 60 lines.
4. Patch the line that disagrees with the docstring, the sibling that does the paired job, or a caller. Typical injected edits: a boolean returned inverted, two arguments or a min and a max swapped, a sign flipped, a name used before it is assigned, a statement moved so a branch never sets it, a mark placed on the wrong side of a name.
5. If the issue names two symptoms, scan the rest of that function for a second site before opening another file.
6. Run the nearest test file: `/opt/miniconda3/envs/testbed/bin/python -m pytest PATH -q --tb=line -p no:cacheprovider`. Confirm pytest collected at least one test.
7. A new failure in a different test means `git checkout -- PATH` for that hunk. Read `git diff` and stop when the snippet and the covering tests pass.

## Zero

No network. No edits to tests, fixtures, `conftest.py`, `pytest.ini`, `tox.ini`, `setup.cfg`, or a pytest section of `pyproject.toml`. No import hooks. No test-runner imports from project source.
