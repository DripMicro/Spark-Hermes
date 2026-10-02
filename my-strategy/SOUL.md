# Put every injected edit back; the issue's expected output decides when you are done

Working code in `/testbed` was mechanically changed, often in more than one place. Restore it. Credit is the share of broken checks that pass again, so each restored site pays and half a fix pays half. One test that used to pass and now fails scores zero. An untouched tree scores zero. Nobody answers questions.

## This page overrides the runtime notes

Those notes say to gather context before acting. Here the order is the reverse: edit, then verify. You have about 25 tool calls and a token budget that every printed line eats again on every later call. Three things end a run early:

- a reply with no tool call. Until you stop, every reply is a tool call. The moment you know a corrected line, the next call applies it;
- one very long stretch of reasoning. Think in a few sentences, then act;
- the same command or the same read about five times. Change something on every call.

By tool call 6 a file under `/testbed` has been changed.

## Already known

- The tree is `/testbed`. Packages sit either at `/testbed/PKG/` or at `/testbed/src/PKG/`: find paths with grep, never guess them. Stay inside `/testbed` and `/tmp`. Do not list, read or run anything anywhere else, not even `ls`: the grader lives out there and touching it scores zero.
- No clean copy of the code exists outside `/testbed`. Installed packages and any other directory hold the same broken code. Never `find /`.
- Git holds one commit and that commit already contains the injected edits. `git log`, `git show`, `git blame` and `git stash` cannot tell you what the code used to be. "It was like this in the first commit" proves nothing. `git diff` shows your own edits and only that.
- Do not reconstruct the upstream file from memory. The evidence is: the issue's expected output, the callers, the sibling functions, the tests still in the tree, and for sqlglot the rendered reference described below. A docstring may have been edited along with the code.
- The interpreter that has the project and pytest is `/opt/miniconda3/envs/testbed/bin/python`. The `python` on `PATH` does not. Use the full path.
- Tools: `terminal`, `read_file`, `search_files`, `patch`, `write_file`, called by exactly those names. There is no `bash`, `grep`, `Read` or `Edit` tool. Do not call `tool_search`, `tool_call` or `tool_describe`. Do not open skills. If a result says a tool is "not a deferrable tool" or warns about a loop, the next call is plain `terminal` doing the same job.
- Leave the `timeout` argument of `terminal` out. It is in seconds; a large number pushes the command into the background and you lose calls waiting for it. Never `sleep`.
- A missing import is normal. Do not pip, conda, or apt. One install ends the episode at zero.
- If `patch` cannot write the file, once: copy it to `/tmp/w.py`, patch that copy, copy it back. No `sudo`, no `chmod`.

## Loop

1. Count the symptoms. Each wrong value, error or behaviour the issue lists is one line of a work list, and each usually has its own injected site. Keep the list to the end. The issue's explanation of the cause is a guess; its snippet and expected output are facts.
2. Grep the name from the issue, outside tests: `grep -rn "NAME" /testbed --include='*.py' | grep -v /tests/ | head -20`. One search per name.
3. Write the issue snippet to `/tmp/r.py` with `write_file`, copying its names and paths exactly. Run `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -n 25`. No snippet: call the named function with the values the issue states and print the result. The last `/testbed` frame of the traceback, or the function that returns the wrong value, is the suspect.
4. Read only the suspect function, at most 60 lines, with the offset taken from `grep -n`. If the whole file is under 120 lines, read it once and never again.
5. Go through it statement by statement: does this line agree with the function's name, its callers and its siblings? Patch the first one that does not, in the next call. Typical injected edits:
   - a boolean returned inverted, a comparison flipped, a `not` added or dropped;
   - two arguments, two assignments or a min and a max crossed;
   - a sign flipped or a constant nudged by one (`- 1`, `+ 1`, `<` for `<=`, a slice bound);
   - a name used before it is assigned, or a bare `pass` where work belongs: the line was deleted, write it back above its first use;
   - a loop, an `if` guard or a `try`/`except` fallback removed, so one item is handled where all should be, or bad input is processed where it used to be skipped or rejected;
   - a `return` or `raise` moved up so the lines after it never run;
   - a method the callers use that is gone: write it back in the shape of its siblings.
6. Nothing stands out but the result is wrong: the whole body was rewritten to look plausible. Stop reading. Write the smallest body that does what the name, the callers and the issue require, using the helpers the neighbouring functions use, and let the repro judge it.
7. Rerun `/tmp/r.py` after every patch and compare it with the issue's expected output line by line. See the next section before doing anything else.
8. Run the nearest test file: `/opt/miniconda3/envs/testbed/bin/python -m pytest PATH -q -x --tb=line -p no:cacheprovider 2>&1 | tail -n 15`. Confirm pytest collected at least one test. The tests that expose the bug were removed, so a green run only says you broke nothing.
9. A new failure in a test that passed before means your last hunk is wrong: undo that hunk with `patch`, not the whole file, and keep the earlier fixes. Read `git diff | head -60` and stop with one line when every symptom on the list is gone and the covering tests pass.

## A line that is still wrong is another injected site

This is where runs are lost. After a fix, the repro prints most of the expected output and one value is still off, for example 5 where the issue says 6.

- That line is a second injected edit. It is not original behaviour, however natural the code looks and however long git says it has been there.
- Find it in the next call: the getter, property, helper or sibling method that produces exactly that value. Look in the same function first, then the same class, then the same file, then the files beside it in the same package directory (two dialects, two formats, two halves of one parser): `grep -rn "NAME" THAT_DIR | head -20`.
- Patch it in the call after that, so the code returns what the issue expects. The simplest reading wins: a property returns the stored value, a length is not shortened, a pair is not crossed.
- The only check allowed first is one grep of the kept tests for that attribute or function name. If no kept test pins the current value, patch. If one does, the wrong site is somewhere else on the path: follow the value one step back.

Clock: two calls in a row without an edit while the repro still differs from the expected output means the next call is a `patch` of your best candidate. A wrong candidate costs one call to revert. Deliberating costs the task.

## sqlglot: the tree carries a rendered reference

Only when the project is sqlglot. `/testbed/docs/sqlglot/` mirrors the package as rendered pages, and each page prints the source of its module with line numbers: `sqlglot/optimizer/simplify.py` is shown by `docs/sqlglot/optimizer/simplify.html`, a dialect by `docs/sqlglot/dialects/NAME.html`. Those pages were not touched by the injected edit. Use them straight after the repro, before any long reading:

1. `cd /testbed && ls docs/sqlglot/optimizer docs/sqlglot/dialects | head -40` if you are unsure the page exists.
2. Turn the page into text once: `/opt/miniconda3/envs/testbed/bin/python -c "import re,html,sys; open('/tmp/d.txt','w').write(html.unescape(re.sub(r'<[^>]+>','',open(sys.argv[1]).read())))" docs/sqlglot/optimizer/simplify.html`
3. `grep -n "def FUNC" /tmp/d.txt | head -3`, then print that function only: `sed -n 'A,Bp' /tmp/d.txt` with a window of at most 60 lines. Each line starts with its line number in the source file, so the same window of the real file is `sed -n 'A,Bp'` on those numbers.
4. Compare the two and patch the real file so the suspect function reads like the reference. Change only the lines that differ, and only in the functions the symptoms point at. Never print the whole page or the whole text file: they are huge.
5. Rerun the repro. A symptom still left means a second function or a sibling module: repeat for that one.

If the page is missing or does not contain the function, go back to the loop. For every other project there is no reference: reason from callers and siblings.

## Where tests live

- python-docx, python-pptx, cantools, marshmallow: source under `src/`, tests under `tests/` following the source layout.
- gpxpy: one test file, `test.py`, at the root. Select with `-k NAME`.
- sqlglot: `tests/test_optimizer.py`, `tests/test_parser.py`, `tests/dialects/test_NAME.py`; expected results in `tests/fixtures/`, which you never edit.
- astroid, sqlparse, pygments, oauthlib: package at the root, tests under `tests/`. Output is compared as exact text, so spacing and wording matter.

## Small outputs

Every command that can print more than a screen ends in `| head -40` or `| tail -n 25`. No `cat` of a source file, no `read_file` without a limit, no `sed -n` window wider than 60 lines, never a test file by the hundred lines. Find the line number with `grep -n` first. Never run the whole suite: one test file, or `-k NAME`. A data or fixture file is read with `grep -n` for the one value you need.

## Zero

No network. No edits to tests, fixtures, golden files, `conftest.py`, `pytest.ini`, `tox.ini`, `setup.cfg`, or a pytest section of `pyproject.toml`. No import hooks, and no `pytest`, `inspect`, `importlib`, `subprocess`, `exec` or `eval` in the fix. Never leave the tree more broken than you found it: a partial fix that breaks nothing is worth more than a full fix with one regression.
