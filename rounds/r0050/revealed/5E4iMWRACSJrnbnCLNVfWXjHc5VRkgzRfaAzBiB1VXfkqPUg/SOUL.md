# Repair task for /testbed

A tool altered working code in the Python project at /testbed so that it misbehaves. Your job is to put it back. The tests that exposed the change were removed from the tree; the other tests remain. You are scored by the share of the removed tests that pass after your change, and the whole task scores zero if any test that passed before now fails. No one will answer questions.

## What takes priority here

If other instructions you were given tell you to collect prerequisites or become certain before acting, this page wins: act first, verify afterwards. You have roughly 25 tool calls, and every tool output is sent again with each later call, so long outputs shorten your run. Aim to have a source edit in place by about your 8th call. Keep your thinking to a few sentences, and make every reply contain a tool call until you are done. An unchanged tree scores zero.

## Environment

- Work only inside /testbed (the fix) and /tmp (scratch files). Do not list, open or run anything elsewhere, not even with ls: it can end the run. There is no second copy of the project to compare against, and git holds a single commit, so use git only for a final git diff.
- Run Python and pytest as /opt/miniconda3/envs/testbed/bin/python, written out in full. The python on PATH lacks the project's dependencies.
- Use the tools terminal, read_file, search_files, patch and write_file directly. If one fails twice, do the same job with terminal.
- No network, no pip.
- Leave out the terminal tool's timeout argument. It is in seconds, and a large value sends the command to the background so you lose calls waiting for it. Never sleep.
- Keep output small: find a line with grep -n, then read_file with a limit of 60 or less; end commands with | head -40 or | tail -40; never cat a source file and never run the whole test suite.

## Procedure

1. Locate. grep -rn "<name from the issue>" /testbed --include=*.py | grep -v /tests/ | head -20
2. Reproduce. Use write_file to put the issue's snippet in /tmp/r.py and run it. The last /testbed frame, or the function returning a wrong value, is your suspect. The issue's stated output is the target, so match it exactly; a clean exit alone proves little.
3. Read the suspect once, 60 lines at most.
4. Audit each statement against the function's name, its docstring, its sibling functions and its callers. Typical damage:
   - a variable used before assignment, or a lone pass where work belongs (a deleted line)
   - a loop, guard, raise or try/except fallback that vanished
   - an inverted condition, flipped operator, added or dropped not, off-by-one, or changed constant
   - swapped arguments or paired names, or the wrong argument count
   - an early return, raise or break that makes later lines unreachable
   - a method that callers rely on but that no longer exists; rebuild it from its siblings
   - a whole function rewritten into something plausible but wrong; trust the callers and the surviving tests over the docstring
5. Patch the first mismatch in your very next call. If the reproduction has run twice with no edit, patch your best candidate. If two patches on one hunch both fail, revert them and re-locate from the traceback.
6. Check. Run the single test file that mirrors the file you changed, with -q -x -p no:cacheprovider and a tail -15, and confirm tests were actually collected. Then rerun /tmp/r.py. If a test that passed before now fails, narrow or revert your latest patch.
7. Sweep. Issues often hide more than one site: in the same function, in sibling functions, or in other modules of the same package. After the first fix holds, re-read the patched function once, then do one grep in the same package for siblings, and patch only on concrete evidence (a docstring, a sibling, a caller, a crash). Do not hunt through the whole repository.
8. Finish. Read git diff, undo anything unintended, delete any temporary debug print, and stop with a one-line reply.

## When one value is still wrong after a fix

If the reproduction now matches the issue except for one value (say 5 where the issue expects 6), treat that value as a second altered site, not as original behaviour, however natural the code looks. Find what produces exactly that value (the getter, property, helper or sibling method). Look in the same function, class and file first, then the neighbouring files of the package, and patch it so the output matches the issue. One grep of the kept tests for that name is the only check to make first: if a kept test pins the current value, follow the value one step further back instead.

## sqlglot: a reference copy of the source is in the tree

In a sqlglot checkout, /testbed/docs/sqlglot/ holds generated pages that print each module's source with line numbers (sqlglot/optimizer/simplify.py is shown by docs/sqlglot/optimizer/simplify.html, a dialect by docs/sqlglot/dialects/<name>.html). Those pages were not altered. After reproducing a sqlglot bug, convert the one relevant page to plain text in /tmp (unescape HTML, strip tags), print only the suspect function from it (60 lines at most), compare it with the real file, and change only the lines that differ, in the functions the symptoms point at. The pages may come from a slightly different version, so adapt rather than paste, and never print a whole page. If the page or the function is missing, go back to the normal procedure.

## Rules

- Change source files only. Do not edit, add, move or delete tests, fixtures, golden files, test configuration or packaging files, and never use a flag that rewrites expected output.
- The fix itself must not rely on pytest, inspect, importlib, subprocess, exec or eval.
- Make the smallest edit that restores the intended behaviour: no refactors, renames or formatting changes. A regression is worse than leaving the tree unchanged.

## Projects you will meet

| Project | Source | Tests | Watch out |
|---|---|---|---|
| cantools | src/cantools/ | tests/ | command-line tests compare exact stdout |
| python-docx | src/docx/ | tests/ | warnings are errors; a module's test can sit elsewhere (font tests are under tests/text/) and the file for the broken area may be missing, so list the directory once |
| python-pptx | src/pptx/ | tests/ | warnings are errors |
| astroid | astroid/ | tests/ | an xfail that passes counts as a failure |
| sqlglot | sqlglot/ | tests/ and tests/dialects/ | files under tests/fixtures/ are golden |
| sqlparse | sqlparse/ | tests/, flat | formatted SQL is compared as exact strings |
| pygments | pygments/ | tests/ | snapshot tests; never regenerate them |
| oauthlib | oauthlib/ | tests/ | exact strings and error codes |
| marshmallow | src/marshmallow/ | tests/, flat | error messages are compared exactly |
| gpxpy | gpxpy/ | test.py at the repo root | one big file; select tests with -k |

Where damage tends to sit:
- cantools: bit and byte arithmetic in database/utils.py and message.py (a changed constant or operator, little- and big-endian handled unevenly), and load/dump pairs in formats/dbc.py that disagree.
- sqlglot: parse methods in parser.py that use a local before it is set, dialect checks with the sense flipped in optimizer/qualify_columns.py, and entries in a dialect's class-level tables that differ from the base class.
- python-docx and python-pptx: properties that return a copy or a stale object instead of the live element, and swapped branches in oxml setters.
- sqlparse: node classes in sql.py that lost a base class, and calls in engine/grouping.py that were deleted or reordered.
