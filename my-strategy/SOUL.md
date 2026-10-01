# Put every injected edit back; the issue's expected output decides when you are done

Working code in `/testbed` was mechanically changed, often in more than one place. Restore it. Credit is the share of broken checks that pass again, so each restored site pays and half a fix pays half. One test that used to pass and now fails scores zero. An untouched tree scores zero.

## This page overrides the runtime notes

Those notes say to gather context before acting. Here the order is the reverse: edit, then verify. You have about 25 tool calls and a token budget that every printed line eats again on every later call. A reply with no tool call ends the run. Until you stop, every reply is a tool call. The moment you know a corrected line, the next call applies it. Think in a few sentences. Do not repeat the same command five times.

By tool call 6 a file under `/testbed` has been changed.

## Already known

- The tree is `/testbed`. Stay inside `/testbed` and `/tmp`. Do not list or read anywhere else.
- Git holds one commit and that commit already contains the injected edits. `git log`, `git show`, `git blame` and `git stash` cannot tell you what the code used to be. "It was like this in the first commit" proves nothing. `git diff` shows your own edits and only that.
- The original source is not on this machine and you cannot recall it reliably. Do not reconstruct the upstream file from memory. The evidence is: the issue's expected output, the callers, the sibling functions, the docstring, the tests still in the tree.
- The interpreter that has the project and pytest is `/opt/miniconda3/envs/testbed/bin/python`. The `python` on `PATH` does not. Use the full path.
- Tools: `terminal`, `read_file`, `search_files`, `patch`, `write_file`. Do not call `tool_search`. Do not open skills. This page is the whole strategy.
- A missing import is normal. Do not pip, conda, or apt. One install ends the episode at zero.
- If `patch` cannot write the file, once: copy it to `/tmp/w.py`, patch that copy, copy it back. No `sudo`, no `chmod`.

## Loop

1. Grep the name from the issue, outside tests: `grep -rn "NAME" /testbed --include='*.py' | grep -v /tests/ | head -20`.
2. Write the issue snippet to `/tmp/r.py` with `write_file`, copying its names and paths exactly. Run `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -n 25`. No snippet: call the named function with the values the issue states and print the result.
3. Read only the function the traceback or the wrong return points at, at most 60 lines. If the whole file is under 120 lines, read it once and never again.
4. Patch the line that disagrees with the docstring, the sibling that does the paired job, or a caller. Typical injected edits: a boolean returned inverted, two arguments or a min and a max swapped, two assignments crossed, a sign flipped, a constant nudged by one (`- 1`, `+ 1`, `<` for `<=`), a name used before it is assigned, a statement moved so a branch never sets it, a deleted loop or guard, a mark placed on the wrong side of a name.
5. Rerun `/tmp/r.py` after every patch and compare it with the issue's expected output line by line. See the next section before doing anything else.
6. Run the nearest test file: `/opt/miniconda3/envs/testbed/bin/python -m pytest PATH -q --tb=line -p no:cacheprovider 2>&1 | tail -n 15`. Confirm pytest collected at least one test. The tests that expose the bug were removed, so a green run only says you broke nothing.
7. A new failure in a test that passed before means your last hunk is wrong: undo that hunk with `patch`, not the whole file, and keep the earlier fixes. Read `git diff | head -60` and stop with one line when the repro prints the expected output and the covering tests pass.

## A line that is still wrong is another injected site

This is where runs are lost. After a fix, the repro prints most of the expected output and one value is still off, for example 5 where the issue says 6.

- That line is a second injected edit. It is not original behaviour, however natural the code looks and however long git says it has been there.
- Find it in the next call: the getter, property, helper or sibling method that produces exactly that value. It is usually in the same class or the same file as the first site.
- Patch it in the call after that, so the code returns what the issue expects. The simplest reading wins: a property returns the stored value, a length is not shortened, a pair is not crossed.
- The only check allowed first is one grep of the kept tests for that attribute or function name. If no kept test pins the current value, patch. If one does, the wrong site is somewhere else on the path: follow the value one step back.
- Words in the issue such as "also", "additionally", "as well", a list of symptoms, or two different wrong values mean at least that many sites. Count the symptoms, and count your patches against them.

Clock: two calls in a row without an edit while the repro still differs from the expected output means the next call is a `patch` of your best candidate. A wrong candidate costs one call to revert. Deliberating costs the task.

When every line of the repro matches, look once at the other methods of the class you edited for the same kind of edit, and patch only a concrete contradiction with the callers.

## Small outputs

Every command that can print more than a screen ends in `| head -40` or `| tail -n 25`. No `cat` of a source file, no `read_file` without a limit, no `sed -n` window wider than 60 lines, never a test file by the hundred lines. Find the line number with `grep -n` first. Never run the whole suite: one test file, or `-k NAME` when the project keeps its tests in a single big file. A data or fixture file is read with `grep -n` for the one value you need.

## Zero

No network. No edits to tests, fixtures, golden files, `conftest.py`, `pytest.ini`, `tox.ini`, `setup.cfg`, or a pytest section of `pyproject.toml`. No import hooks. No test-runner imports from project source. Never leave the tree more broken than you found it: a partial fix that breaks nothing is worth more than a full fix with one regression.
