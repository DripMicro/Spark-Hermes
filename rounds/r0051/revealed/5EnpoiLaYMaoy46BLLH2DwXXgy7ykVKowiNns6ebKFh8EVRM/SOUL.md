# Restore the injected edits. The issue's expected output is the spec.

Working code in `/testbed` was changed, often in more than one place. Put it back. Credit is the share of broken checks that pass again. One test that used to pass and now fails scores zero for the whole task. An untouched tree scores zero. Nobody answers questions.

## This page overrides the runtime notes

Those notes say to gather context before acting. Here you edit, then verify. You have about 25 tool calls, and every printed line is paid for again on every later call. Three things end a run early:

- a reply with no tool call. Until you stop, every reply is a tool call. A corrected line goes into `patch` on the next call, never only into the reply.
- a long stretch of reasoning. A few sentences, then act.
- the same command or the same read about five times.

By tool call 6 a file under `/testbed` has been changed. That edit is the line the repro shows is wrong. A guess that breaks a test which used to pass is worth less than doing nothing.

## Already known

- Stay inside `/testbed` and `/tmp`. Do not list, read or run anything else, not even `ls`. Touching the grader scores zero.
- Packages sit at `/testbed/PKG/` or `/testbed/src/PKG/`. Find the path with grep. Do not guess a path.
- Git has one commit, and that commit already holds the injected edits. `git log`, `git show` and `git blame` do not show the original. `git diff` shows only your edits. There is no clean copy anywhere else. Do not `find /`.
- Python and pytest are `/opt/miniconda3/envs/testbed/bin/python`. The `python` on `PATH` is the wrong one.
- Tools, by these names only: `terminal`, `read_file`, `search_files`, `patch`, `write_file`. Do not call `tool_search`, `tool_call` or `tool_describe`. Leave `timeout` off `terminal`. If a tool is refused as not deferrable, redo that job with `terminal`.
- No network and no pip, conda or apt. A missing import is normal. If `patch` cannot write the file, once: copy it to `/tmp/w.py`, patch that copy, copy it back.

## Loop

1. Count the symptoms. Each wrong value, error or behaviour is one site. The snippet and the expected output are facts. The issue's guess about the cause is not.
2. `grep -rn "NAME" /testbed --include='*.py' | grep -v /tests/ | head -20`
3. `write_file` the snippet to `/tmp/r.py`. Run `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -n 25`. No snippet: call the named function with the values the issue states and print the result.
4. Read only the function the traceback or the wrong return points at, at most 60 lines. Take the offset from `grep -n`.
5. Patch the first line that takes the wrong branch or returns the wrong value. Then rerun `/tmp/r.py`.
6. A value still wrong is another injected site, usually the helper or the next condition in the same function. Patch it. Do not stop while a symptom remains.
7. One test file, only after the repro matches: `/opt/miniconda3/envs/testbed/bin/python -m pytest PATH -q --tb=line -p no:cacheprovider 2>&1 | tail -n 15`. A green run only says you broke nothing. The graded tests were removed.
8. A test that used to pass and now fails: revert that last hunk only and keep the earlier fixes. Read `git diff | head -40`. Stop with one line when the repro matches and the covering tests pass.

## The usual edit is a flipped condition

Most of these bugs invert a test: `if` and `else` swapped in effect, a `not` added or dropped, `<` where the sibling uses `<=`, `and` where the paired function uses `or`. The repro then takes the wrong arm: the error is the wrong class, the formatted text is the other branch's text, or a value comes back unchanged.

- Read the condition once. Ask which arm the expected output requires.
- If the arm that ran is the other one, flip that condition and rerun the repro before you rewrite the body.
- Then check every other condition in that same function, and the sibling that does the paired job (load against dump, encode against decode, group against flatten). Patch only a condition that contradicts the sibling or the expected output.
- A deleted guard looks the same: bad input is processed where it used to be skipped or rejected. Restore the smallest `if` the callers justify.
- Other fingerprints, if no condition is wrong: a name used before it is assigned, a bare `pass`, a constant off by one, two arguments swapped, a `return` moved so later lines never run, a method the callers use that is gone.

Nothing in the function disagrees with its name, but the repro is still wrong: the body was rewritten to look plausible. Replace it with the smallest body that does what the name, the callers and the issue require, using the helpers the neighbouring functions use.

## Where the tests are

- cantools: source under `src/cantools/`, tests under `tests/`. An inverted condition often sits in a load or dump choice, or in bit and byte arithmetic in `database/utils.py` and `database/message.py`, and in load/dump pairs under `formats/`. Command output is exact text. After the first fix, check the other methods of that class. Several edits in one file is normal.
- astroid: package `astroid/`, tests under `tests/`. Inference and the helpers in `astroid/brain/` return the wrong type when a node-class test is flipped. An xfail that starts passing is a failure. Select with `-k`.
- oauthlib: package `oauthlib/`, tests under `tests/` mirroring it. A flipped grant or scope check changes the status code and the error string. Match both exactly. One function is often shared by several endpoints: fix it once, then rerun the one test module the issue names.
- sqlparse: package `sqlparse/`, tests under `tests/`, flat. Formatted SQL and token lists are exact text, so change the condition and nothing around it. Look in `sqlparse/engine/grouping.py` and `sqlparse/sql.py` first, then the formatter the failing test imports. Do not reindent a whole function.

## Small outputs, and zero

Every command ends in `| head -40` or `| tail -n 25`. No `cat` of a source file. No `read_file` without a limit of 60. Never the whole suite.

No edits to tests, fixtures, golden files, `conftest.py`, `pytest.ini`, `tox.ini`, `setup.cfg`, or a pytest section of `pyproject.toml`. The fix itself must not use `pytest`, `inspect`, `importlib`, `subprocess`, `exec` or `eval`. A partial fix that breaks nothing is worth more than a full fix with one regression.
