# Repair an injected bug in /testbed

A program mutated working code in the Python project at `/testbed`. Undo the mutation. The tests that caught
it were deleted from the tree; the rest of the suite stays. You earn the share of those deleted tests that
pass afterwards, and zero for the whole task if any test that passed before now fails. Nobody will reply to
questions. When you are finished, answer with one short line and no tool call.

## How to read the rest of your prompt

Later sections of your prompt ask for prerequisite checks and certainty before acting. For this job, act
first and verify after: an unedited tree always scores zero, a careful wrong edit costs the same. The token
budget allows roughly 25 to 30 tool calls, because every earlier output is re-sent with each new call.
Have a source edit in place by call 8. Keep each reasoning step to a few sentences: a reply cut off for
length, or a reply without a tool call, ends the run where it stands.

## Machine facts (already verified, do not re-check)

- Python with the project's dependencies and pytest: `/opt/miniconda3/envs/testbed/bin/python`. The bare
  `python` lacks them. Type the full path every time.
- Tools: `terminal`, `read_file`, `write_file`, `patch`, `search_files`. Call them by name directly. There
  is no `bash`, `Bash`, `Read`, `Edit`, `grep` or `rg` tool, and `tool_call`, `tool_search`, `skill_view`,
  `skill_manage` only waste calls. After any unknown-tool error, use `terminal`.
- Never pass the `terminal` timeout argument (it is seconds; a large value backgrounds the command and you
  lose calls waiting). Never `sleep`.
- Git holds one commit: history, `git log`, `git show` and `HEAD~1` reveal nothing. `/opt/sh-pristine` and
  site-packages hold the same broken code. Searching the filesystem outside `/testbed` finds nothing useful.
- Batch independent look-ups (a grep plus a read, two reads) into one reply; it saves a full re-send.
- Eight failures of one file tool (`patch`, `read_file` or `search_files`) end the run, as do five identical
  calls in a row. `read_file` output prefixes each line with `N|`: never copy that prefix into a patch.
  After one failed patch, re-read those exact lines and copy `old_string` from that output.

## Lines that score zero

- Any path or command naming `/ep` or `/runner`; network of any kind (`pip`, `curl`, `git fetch`).
- Editing or adding tests, `conftest.py`, fixtures, golden or snapshot files, `setup.py`, `setup.cfg`,
  `pyproject.toml`, `tox.ini`, `pytest.ini`, `.coveragerc`. Writing anywhere except `/testbed` and `/tmp`.
- A fix that adds an import of `inspect`, `importlib`, `subprocess`, `threading`, `signal`, `gc`, `ctypes`,
  `builtins` or `pytest`, calls `eval`, `exec` or bare `compile`, or touches `sys.modules`. If the right fix
  seems to need one of these, you have the wrong fix.

## Procedure

1. **Ledger.** List each concrete symptom in the issue (wrong value, exception, missing behaviour). The
   issue's expected output is the specification, character for character. Several symptoms usually mean
   several mutated sites; each one you fix earns its share.
2. **Locate.** `grep -rn "<name from the issue>" /testbed --include=*.py | grep -v /tests/ | head -20`.
3. **Reproduce.** `write_file` the issue's snippet (or a minimal call) to `/tmp/r.py`, printing the values
   the issue talks about. Run `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -30`.
   The deepest `/testbed` frame, or the first function returning a wrong value, is the suspect.
4. **Read the suspect** with `read_file` (offset from `grep -n`, limit at most 60) or `sed -n 'A,Bp'`.
   In the same reply grep its callers or its siblings. Never read a whole file; never `cat` source; end
   long commands with `| head -40` or `| tail -40`.
5. **Diagnose** against the mutation catalogue below. Compare each statement with the function name, its
   docstring, its callers, sibling functions that do the mirror job, and the issue.
6. **Patch the first certain mismatch in your next call.** If the repro has run twice with no edit, patch
   your best candidate. Restore the original in place: no refactors, renames, new helpers, new files or
   workarounds in a caller. Only the files the bug touched are graded, so an edit elsewhere is discarded.
7. **Re-run the repro** and compare with the expected output line by line. Still one value wrong: that is a
   second mutated site; find what produces that value (getter, helper, sibling, same class or package) and
   patch it. Two failed patches on one idea: revert them and re-locate from the traceback.
8. **Regression check.** The test file mirroring your module was often deleted with the broken tests, so find
   survivors: `grep -rln "<module or symbol>" /testbed/tests | head` (gpxpy keeps no tests at all). Run one
   to three of them: `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <files> -q -x -p no:cacheprovider 2>&1 | tail -15`.
   Never the whole suite. A failure caused by your edit: narrow or revert that edit. Green tests prove only
   that you broke nothing visible; the repro matching the issue is the real check.
9. **Finish.** `cd /testbed && git diff`, remove debug prints and anything unintended, then stop with one line.

## Mutation catalogue (what the injector does and how it looks)

- **Changed operator or constant**: `<` for `<=`, `+` for `-`, `and` for `or`, `is` for `is not`, an index
  or slice off by one, a wrong default, shift or mask, byte order or unit. Swapped operands
  (`b - a`), swapped arguments, or two paired names exchanged.
- **Inverted branch**: an `if` whose body and `else` body were exchanged, or a dropped or added `not`.
- **Removed statement**: a name used before any assignment, a lone `pass`, a loop that handles one item, a
  missing guard (`None` or empty check, a `raise` for bad input), a missing `try/except` fallback, a value
  computed but never returned or stored, a missing wrapper call.
- **Shuffled statements**: correct lines in the wrong order, such as a `return` before the work, a use
  before the assignment, a guard after the code it protects, a docstring that is not the first statement.
- **Removed method**: callers use a method or property that no longer exists; rebuild it from its siblings
  and the callers' expectations. But if a similar name exists (`after_x` exists, callers call `before_x`),
  the call site was probably altered instead: prefer fixing the single changed line.
- **Rewritten function**: the body reads plausibly but contradicts its name, docstring, callers or sibling
  functions, or it fakes the work. Rewrite the smallest body that satisfies them, reusing the helpers the
  siblings use and keeping the signature, return type and exception types.
- **Combined**: several of the above in one file or across a package's sibling modules. After the first fix
  holds, re-read the patched function once and check its siblings for the same kind of damage.

## Projects

| Project | Source | Notes |
|---|---|---|
| astroid | `astroid/` | huge modules (`nodes/`, `brain/`, `inference*`): grep first, read 40 lines; an xfail that passes is a failure |
| cantools | `src/cantools/` | bit and byte math in `database/utils.py`, `can/message.py`, `can/signal.py`; format load/dump pairs in `database/can/formats/` must agree; CLI output in `subparsers/` compared exactly |
| sqlglot | `sqlglot/` | see the reference copy below; tests in `tests/` and `tests/dialects/`; `tests/fixtures/` is golden |
| python-docx | `src/docx/` | oxml setters and properties; warnings are errors, so introduce none |
| python-pptx | `src/pptx/` | same layout and warning rule as python-docx |
| oauthlib | `oauthlib/` | exact error strings, status codes and parameter order matter |
| marshmallow | `src/marshmallow/` | error messages compared exactly |
| sqlparse | `sqlparse/` | grouping in `engine/grouping.py`, token classes in `sql.py`; formatted SQL compared as strings |
| gpxpy | `gpxpy/` | no tests in the tree; the repro is your only check |
| pygments | `pygments/` | lexer token streams compared exactly |

**sqlglot reference copy.** `/testbed/docs/sqlglot/` holds generated pages showing each module's original
source with line numbers (`sqlglot/parser.py` is `docs/sqlglot/parser.html`, a dialect is
`docs/sqlglot/dialects/<name>.html`); the mutation did not touch them. After the repro, write a small
`/tmp` script that unescapes the HTML entities and strips the tags of that one page into a text file under
`/tmp`, `grep -n` the suspect function there, print at most 60 lines, and change only the lines that differ
in the real file. The pages may be a slightly different version: adapt, do not paste blindly. If the page or
the function is missing, continue with the normal procedure.

Best outcome: every mutated site restored and nothing else changed. Next: some sites restored, nothing
broken. A regression is worse than leaving the tree untouched.
