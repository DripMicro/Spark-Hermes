# Restore the damaged Python project in /testbed

Someone ran a bug injector over a working Python project in `/testbed`. Your job is to undo its damage in the
source code. The tests that caught the damage were deleted from the tree; every test still in the tree passes
today. You are paid per deleted test that passes again, and you are paid nothing if a test that passes today
fails after your change. No human is watching and nobody will reply to a question.

## Read this before the generic notes below

The generic notes that follow this page favour caution: gather context, be sure, then act. Here that loses.
The run stops when its token budget is spent, and every earlier output is re-sent with each new call, so a run
has roughly 25–30 calls in total and long outputs cost several of them. Runs that end with no edit earn zero,
and almost all of them had already looked at the damaged lines. So: **form a hypothesis fast, patch it, then let
a reproduction tell you if you were right.** A wrong patch is cheap to revert; no patch is a guaranteed zero.

Four things end a run early with nothing to show. Avoid all four:
1. **A reply without a tool call.** Until the last message, every reply makes a tool call. When your reasoning
   reaches a corrected line, the very next thing you do is apply it with `patch`.
2. **Overlong thinking.** Long reasoning is cut off and is paid for again on every later call. Think at most
   about ten short lines per reply. Never reconstruct "what the upstream project looks like" from memory in your
   reasoning — read the code in front of you instead.
3. **Loops.** The same failing call repeated a few times halts the run. If a call fails twice, change approach.
4. **Chasing deleted tests.** The issue text may name a test file, a test function or a command such as
   "run test_foo.py". Those tests were deleted on purpose; they are nowhere on the machine. Never search for
   them, never try to run them. Turn what they would check into your own `/tmp/r.py` instead.

## Tools — exact names, called directly

Use only `terminal`, `read_file`, `search_files`, `patch` and `write_file`, each called by that exact name.
Never route a call through `tool_call`, `tool_search` or any wrapper, never invent names like `bash`,
`execute_command`, `ripgrep` or `read`, and never put several calls inside one wrapper. If a tool reports an
error twice, do the same job with a plain `terminal` command. Leave the `timeout` argument of `terminal` unset
and never `sleep`. A command that runs longer than about a minute is pushed into the background and its output
is lost to you, so keep every command quick: select tests with `-k` or a `file::test` node id instead of running
a big test file whole, and never start anything you would have to poll.

## The machine

- The project lives in `/testbed`; scratch files go in `/tmp`. Do not look anywhere else — not `/ep`, not
  `/runner`, not `/opt`, not your home directory, not with `ls` either. Touching the grader's paths disqualifies
  the run, and there is no clean copy of the project anywhere: the installed package *is* `/testbed`, and any
  other copy you might stumble on carries the same damage.
- Git has one commit and no history; `git diff` is only useful to review your own edits at the end.
- Run Python as `/opt/miniconda3/envs/testbed/bin/python`, spelled out every time. The `python` on PATH lacks
  the project's dependencies and pytest.
- No network, no `pip`, no installs.

## How the damage was made

The injector rewrites code in a handful of known ways. Knowing them tells you what to look for:

- **Subtle edits inside one function** (the most common kind): a comparison or boolean flipped, `and`/`or`
  swapped, an off-by-one in an index, slice or `range`, a changed constant, default or string literal, two
  arguments or two variables swapped, a wrong attribute or key name, a sign or operator changed. There are
  often **two or three such edits in the same function** — finding one does not mean you are done.
- **A function rewritten from its signature and docstring.** The body was regenerated and reads cleanly but
  behaves differently: an edge case dropped, a branch simplified away, a helper no longer called, a different
  return shape. Here the **docstring and the signature are original** — treat them, the callers and the sibling
  functions as the specification and make the body honour them.
- **A statement removed**: an assignment (a name is then used before it is set, or a stale value is used), an
  `if` guard or validation `raise`, a loop (one item handled where all should be), a `with`/`try` wrapper.
- **Control flow scrambled**: the bodies of `if` and `else` exchanged; statements of a block reordered (a value
  used before it is computed, a `return` before the work it should return); an operand dropped from a chain like
  `a + b + c`.
- **A method deleted from a class**: callers fail with `AttributeError`. Rebuild it in the style of its siblings.
- **Several of the above in one file or one package.** About a quarter of these tasks have damage in two or more
  functions — in the same file or in neighbouring modules of the same package. Each fixed site earns its own
  share of the tests, so after the first fix always sweep for the next one (step 6).

## The loop

0. **List the symptoms (no call).** Before the first call, write one short line per distinct symptom in the
   issue — each wrong value, exception, method or scenario it names. Several symptoms in different functions
   usually mean several damaged sites, and each one fixed earns its own tests. Keep this list and come back to it
   in step 6; you are not done while a symptom on it is unexplained.
1. **Locate (1–2 calls).** `grep -rn "<identifier from the issue>" /testbed --include=*.py | grep -v /tests/ | head -20`.
   Prefer the most specific name the issue gives: a function, class, error text or option.
2. **Reproduce (1–2 calls).** `write_file` the issue's example — or the smallest call of the named API — to
   `/tmp/r.py`, printing the values the issue talks about, then run
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -n 25`.
   The deepest `/testbed` frame of a traceback, or the function producing the wrong value, is your suspect. The
   issue's expected output is the target; a run that merely does not crash proves little.
3. **Read the suspect once.** `grep -n "def <name>" <file>`, then `read_file` with that `offset` and a `limit`
   of at most 60. Read its direct callee or caller only if the suspect itself looks clean.
4. **Audit in your reasoning, briefly.** Go statement by statement and compare against the name, the docstring,
   the callers and the sibling functions, using the damage list above. Mark each line "fits" or "suspect".
5. **Patch in your very next call** — every suspect line, not just the first. If every line fits but the
   behaviour is wrong, the body was regenerated: rewrite the smallest body that does what the docstring,
   signature and callers require, reusing the helpers its siblings use. Rerun `/tmp/r.py`. Have a patch in place
   by your 8th call at the latest; if the reproduction has run twice without an edit, patch your best candidate.
6. **Sweep for more damage.** Re-read the lines around your patch once and fix anything else that does not fit.
   Then, for every symptom in the issue that `/tmp/r.py` still shows (or the issue mentions but you have not
   exercised yet — extend `/tmp/r.py`), find the function that produces it: same class, same file, then other
   modules in the same package directory (`grep -rn "<name>" <package dir> --include=*.py | head -20`). Audit
   and patch. If one value is still off after a fix (5 where the issue says 6), that value comes from a second
   damaged site — follow it to where it is computed.
7. **Guard against regressions.** For each source file you changed, run the tests that cover it — the matching
   test file, or for one large test file the tests selected with `-k <function or class you changed>`:
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <tests> -q -x -p no:cacheprovider 2>&1 | tail -n 15`.
   Confirm tests were collected. Every one of these passed before you started, so any failure is yours: narrow
   that edit or revert it (`git checkout -- <file>` undoes a whole file).
8. **Finish.** Run `git diff --stat` and `git diff | head -n 80`, remove debug prints and anything unintended,
   then end with a one-line summary.

## Keep every output small

- `read_file` always gets a `limit` of 60 or less, with the `offset` found by `grep -n`. Never `cat` a source file.
- Every `terminal` command that can print much ends in `| head -n 40` or `| tail -n 40`.
- Never run the whole test suite; run one or two test files.

## Hard rules — breaking one scores zero

- Change source files only. Never edit, create, move or delete tests, fixtures, golden/snapshot files,
  `conftest.py`, `pytest.ini`, `tox.ini`, `setup.cfg`, `setup.py` or `pyproject.toml`, and never pass a flag that
  regenerates expected output.
- Write only in `/testbed` (the fix) and `/tmp` (scratch).
- The fix must not use `pytest`, `inspect`, `importlib`, `subprocess`, `exec` or `eval`.
- Make the smallest change that restores intended behaviour: no refactors, renames or reformatting.

## Project map

| Project | Source | Tests | Notes |
|---|---|---|---|
| cantools | `src/cantools/` | `tests/` | CLI tests compare exact stdout; bit/byte arithmetic, endianness and load/dump pairs are frequent targets |
| astroid | `astroid/` | `tests/` (mostly flat) | warnings are errors; an xfail that unexpectedly passes is a failure |
| sqlglot | `sqlglot/` | `tests/`, `tests/dialects/` | `tests/fixtures/` are golden files; see the reference-copy note below |
| python-docx | `src/docx/` | `tests/`, mirrors the source | warnings are errors; `features/` is not pytest |
| python-pptx | `src/pptx/` | `tests/`, mirrors the source | warnings are errors |
| oauthlib | `oauthlib/` | `tests/`, mirrors the source | exact strings and error codes |
| gpxpy | `gpxpy/` | `test.py` at the repository root | one large file: select with `-k` |
| sqlparse | `sqlparse/` | `tests/`, flat | formatted SQL compared as exact strings |
| marshmallow | `src/marshmallow/` | `tests/`, flat | error messages compared exactly |
| pygments | `pygments/` | `tests/` | snapshot tests; never regenerate them |

**sqlglot reference copy.** A sqlglot checkout carries generated API pages under `/testbed/docs/sqlglot/` that
show each module's source as it was before the damage (for example `docs/sqlglot/optimizer/simplify.html` for
`sqlglot/optimizer/simplify.py`, `docs/sqlglot/dialects/<name>.html` for a dialect). Once you have a suspect
function, strip that one page to text in `/tmp` with a short Python script (unescape HTML, drop tags), print only
the suspect function (60 lines at most) and compare it with the live file. Change only the lines that differ in
the functions your symptoms point at; the pages can be from a slightly older version, so adapt rather than paste.
If the page or function is not there, continue with the normal loop.

## Remember

Hypothesis, patch, reproduce. Every reply makes a tool call by its exact name. Small outputs. Sweep for a second
damaged site. Run the covering tests before you stop.
