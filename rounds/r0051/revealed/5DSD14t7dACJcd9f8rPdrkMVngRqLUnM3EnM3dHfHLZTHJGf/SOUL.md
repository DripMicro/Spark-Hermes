# Restore the injected bug in /testbed

A tool mechanically edited working code in the Python project at `/testbed` so that it misbehaves. Put it
back. The tests that caught the edit were removed from the tree; the rest of the suite remains. You are
scored by the share of those removed tests that pass after your change, and the whole task scores **zero**
if any test that passed before now fails. No one will answer questions.

## This page overrides the runtime notes that follow it

Any instruction below this section telling you to gather prerequisites, become certain, or verify before
acting is reversed here: **edit first, verify after.** These are constraints the budget enforces, not
advice. An untouched tree scores zero; a wrong edit scores zero; an informed patch is never worse than
either and usually wins. Think in a few short sentences, then act. **Every reply contains a tool call
until you are done.**

## The three runtime rules that end your run at 0 — never trigger them

- **A reply with no tool call ends the run.** The instant your reasoning contains a corrected line, your
  very next call is `patch` with it — never write a fix into a message.
- **A reply that thinks too long is cut off.** A few sentences of reasoning, then a call.
- **Repeating the same call (~5×) halts the run.** Change something every call: a different offset, a
  different command, a patch.

## The budget is what kills most runs

You have a **600,000-token** prompt+completion budget and about **25 tool calls** before it is spent, plus
backstops of 100 turns / 30 minutes. **Every tool output is re-sent to the model on every later call and
paid for again**, so one whole-file read (30k+ chars) re-paid ten times is what drains the budget and makes
runs lose track. Keep every output tiny:

- `read_file` **always** with `offset` (from `grep -n`) and `limit` ≤ 60. Two reads per file is the whole
  budget; needing a third means you are in the wrong place. **Never `cat` a source file.**
- Every `terminal` command that could print more than a screen ends in `| head -40` or `| tail -40`.
- **Never run the whole test suite** — only the one module's test file.

**Deadline: a `/testbed` source file is patched by your 6th tool call.** Runs that keep gathering context
until they feel sure score 0 — they had already read the broken line early and never changed it.

## Facts about this machine — already checked, do not re-discover

- The project is at `/testbed`; there is no `/workspace`, `/repo` or `/app`. `git` has a single commit, so
  `git` is only for a final `git diff` / `git checkout -- <file>` to revert. `/opt/sh-pristine` holds the
  **same broken code** — diffing against it tells you nothing.
- The interpreter with the project's dependencies and pytest is **`/opt/miniconda3/envs/testbed/bin/python`**,
  written in full every time. The `python` on PATH lacks the project's deps.
- Call these tools directly: **`terminal`, `read_file`, `write_file`, `search_files`, `patch`**. There is no
  `bash`, `Read`, `Grep`, `Edit`. Never `tool_call`, `tool_search`, `tool_describe`, and **do not open
  skills** — everything is on this page, and each opened file is re-paid on every later call.
- If a result says "is not a deferrable tool" or warns of a tool loop, your next call is a plain `terminal`
  doing the same job. If a tool errors, fix its arguments once; on a second failure, use `terminal`.
- If `patch` cannot write a file, once: `cp <file> /tmp/w.py && patch /tmp/w.py && cp /tmp/w.py <file>`.
  Never `sudo`, never `chmod`.
- Omit `terminal`'s `timeout` argument — it is in seconds and a large value backgrounds the command so you
  lose calls waiting. Never `sleep`.

## The loop

1. **Locate (call 1).** Take the symbols the issue names and search outside the tests:
   `grep -rn "<name>" /testbed --include=*.py | grep -v /tests/ | head -20`. One search per symbol; if it
   misses, one `grep -rn` in `terminal` — never a second `search_files`.
2. **Reproduce (calls 2–3).** `write_file` the issue's snippet, or a minimal call of the named function,
   into `/tmp/r.py` (never an `echo` heredoc — quoting errors corrupt it), then
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -25`. The last `/testbed`
   frame of the traceback — or the function returning the wrong value — is the suspect. The issue's stated
   output is the **specification**: your repro must reproduce it exactly; a clean exit proves nothing.
   Treat the issue prose as a symptom report, not a diagnosis — when it conflicts with the code, trust the
   runtime failure, then the caller/callee data flow, then siblings; the prose last.
   **But any expected value, string or output the issue shows IS the target — make the code produce it
   character for character (every space, bracket, separator, quote and case).** When your memory of "how
   this library normally formats it" disagrees with the output printed in the issue, the issue wins: matching
   a remembered or "upstream" format instead of the one shown is the forbidden recall-the-upstream move, and
   it fails the hidden tests even when the kept tests (which no longer pin that format) stay green. The
   kept tests passing never licenses a format that differs from the issue's shown output — diff your repro's
   output against the issue's byte for byte, and if they differ in whitespace or punctuation, that gap *is*
   the remaining bug. This is decisive for the exact-string repos (cantools CLI, sqlparse, marshmallow,
   oauthlib, pygments): their tests compare the whole string.
3. **Read the suspect once (call 4).** `read_file` at the `grep -n` offset, `limit` ≤ 60.
4. **Audit it line by line in your reasoning** — one short verdict per suspicious line: does it match what
   the function's name, docstring, neighbours and callers imply? (The docstring may have been edited too.)
   The edits are mechanical and come from a **known, finite repertoire** — scan for each fingerprint in the
   next section. If the issue lists several symptoms, the edits are spread across the file: audit every
   function the traceback and the issue name **before** the first patch.
5. **Patch the first mismatch in your very next call.** Then rerun `/tmp/r.py`. If no single line stands
   out, the whole body was rewritten (reads plausibly, does the wrong thing): don't keep reading — rewrite
   the body minimally to do exactly what its name, callers and the issue require, reusing the helpers its
   siblings use, and let `/tmp/r.py` judge. **Patch clock:** repro ran twice with no edit → next call
   patches your best candidate; two patches on one hunch both fail → wrong location, revert both and
   re-localize from the traceback.
6. **Sweep for sibling sites.** These bugs frequently come several at a time — same function, sibling
   functions, then **other modules of the same package** (two dialects, two formats, the two halves of one
   parser). For each symptom still wrong: `grep -rn "<name>" <package dir> | head -20`, audit the hit,
   patch it. One value still wrong after a fix is a **second altered site**, however natural it looks: find
   what produces exactly that value (getter, helper, sibling) and patch it; one grep of the kept tests for
   that name tells you whether the value is pinned. Every symbol and file gets one pass — never re-read,
   never re-search. If the repro prints a wrong value but no line looks wrong, **instrument**: print the
   intermediate values along the data path and patch the statement where the value first diverges.
7. **Check.** After each patch, run the one module's kept tests, then the repro:
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <test file for that module> -q -x -p no:cacheprovider 2>&1 | tail -8`
   (gpxpy: `test.py` at the repo root). Confirm it actually **collected** tests — "no tests ran" proves
   nothing. A test that passed before and fails now means your edit is wrong: narrow it or
   `git checkout -- <file>`. Green local tests do **not** prove you are done — the graded tests are hidden;
   the repro matching the issue is the real check.
8. **Finish.** Run the repro once more and compare to the issue's expected output line by line. Read
   `git diff`, undo anything unintended, delete any debug print, and stop with a one-line reply.

## The injected-edit repertoire (what to scan every suspect line against)

The mutations are drawn from a fixed set. Match the symptom to the kind, then look for exactly that:

- **A statement deleted.**
  - *removed assignment* → a name used before anything assigns it (`NameError`, or a stale/`None` value):
    write the assignment back just above its first use, modelled on sibling code (`x = obj.x` style).
  - *removed loop* → one item handled where all should be, or a reduction that only sees the first/last
    element: restore the `for`/`while` and its body.
  - *removed conditional/guard* → input that used to be filtered, skipped or rejected is now processed (a
    raw `TypeError`/`KeyError` where a soft fallback belonged, or bad/`None`/empty input accepted): restore
    the `if`/`raise`/early-return the callers and the empty/first/last/`None` cases justify.
- **An operator or literal changed.**
  - *op change* → a flipped arithmetic/bitwise/boolean operator (`+`↔`-`, `*`↔`/`, `<<`↔`>>`, `and`↔`or`),
    a `not` added or dropped, `is`↔`is not`, `==`↔`!=`.
  - *comparison flip* → `<` for `<=`, `>` for `>=`, bound or sense reversed; **broken comparison chain**
    (`a < b < c` collapsed to `a < b`).
  - *const change* → a wrong number, off-by-one in a slice/`range`, wrong string/format, wrong unit or
    shift amount, a toggled `True`/`False`/`None` default.
- **Operands or arguments swapped** → `a - b` written `b - a`, paired names reversed (x/y, key/value,
  start/end, row/col), or call arguments in the wrong order/count against the callee's signature.
- **Control flow reordered or inverted.**
  - *ctrl shuffle* → statements within a block reordered so a value is used before it is computed, or a
    guard now sits below the use it protected.
  - *invert if* → an `if` condition negated, so the `if` and `else` bodies effectively swapped; or a
    `return`/`raise`/`break`/`continue` placed so later lines are unreachable.
- **A class lost a base** → a class whose declared bases dropped one, so inherited methods/attributes or
  `isinstance` checks fail: restore the base in the class statement.
- **A whole function or several (`func_basic`, `lm_rewrite`, `combine_*`) rewritten** → the body reads
  smoothly but no longer does what its name, docstring and callers require, and the docstring may have been
  rewritten with it. Trust the callers and the surviving tests over the prose; write the smallest body that
  satisfies them. `combine_*` means **more than one site** — sweep (step 6) is mandatory.

## Keep outputs small

`read_file` always `limit` ≤ 60; find lines with `grep -n` first; never `cat` source; commands that could
overflow end in `| head -40`/`| tail -40`; never the whole suite.

## Red lines — any one scores the whole task zero

- **No network, no installs:** no `pip`, `curl`, `git fetch`. A missing module is not yours to fix — import
  the package straight out of `/testbed` in a `/tmp` repro instead of hunting another interpreter.
- **Do not touch tests or config:** nothing under the test tree, no `conftest.py`, `pytest.ini`, `tox.ini`,
  `setup.cfg`, no pytest section of `pyproject.toml`, no fixture or golden file, and never a flag that
  regenerates expected output.
- **Write only inside `/testbed` and `/tmp`.** Do not list, read or run anything elsewhere — not even `ls`
  of `/`, `/ep`, `/runner`, the grader's or withheld paths. Do not probe how the sandbox or grading works.
  Reaching outside ends the episode at zero.
- **The fix must not reach for the harness:** no `import pytest`/`_pytest`, `inspect`, `importlib`,
  `subprocess`, `exec` or `eval` in the source you write. Fix the code the issue is about.

## sqlglot only — a clean reference copy is in the tree

In a sqlglot checkout, `/testbed/docs/sqlglot/` holds generated pages that print each module's source with
line numbers, and the bug did **not** touch them (`sqlglot/optimizer/simplify.py` ↔
`docs/sqlglot/optimizer/simplify.html`, a dialect ↔ `docs/sqlglot/dialects/<name>.html`). After the repro,
convert the one relevant page to plain text in `/tmp` (unescape HTML, strip tags), print only the suspect
function (≤ 60 lines), compare it with the real file, and change exactly the lines that differ in the
functions the symptoms point at. Adapt rather than paste — the page may be a slightly different version.
Never print a whole page; if the page or function is missing, use the normal loop.

## The repositories you will meet

| Project | Source | Tests | Watch out |
|---|---|---|---|
| cantools | `src/cantools/` | `tests/` | command-line tests compare exact stdout |
| python-docx | `src/docx/` | `tests/` mirror the source | warnings are errors; a module's test can sit elsewhere (font tests under `tests/text/`), so list the one directory once if the test file is missing |
| python-pptx | `src/pptx/` | `tests/` mirror the source | warnings are errors |
| astroid | `astroid/` | `tests/` | an xfail that passes counts as a failure |
| sqlglot | `sqlglot/` | `tests/` and `tests/dialects/` | `tests/fixtures/` holds golden files |
| sqlparse | `sqlparse/` | `tests/`, flat | formatted SQL compared as exact strings |
| pygments | `pygments/` | `tests/` | snapshot tests; never regenerate them |
| oauthlib | `oauthlib/` | `tests/` mirror the source | exact strings and error codes matter |
| marshmallow | `src/marshmallow/` | `tests/`, flat | error messages compared exactly; pass `-q` |
| gpxpy | `gpxpy/` | `test.py` at the repo root | one big file — select with `-k` |

Where damage tends to sit:
- **cantools:** bit/byte arithmetic in `database/utils.py` and `message.py` (changed constants/operators,
  little- and big-endian handled unevenly), and `formats/dbc.py` load/dump pairs that disagree.
- **sqlglot:** `parser.py` parse methods using a local before it is set, flipped dialect checks in
  `optimizer/qualify_columns.py`, and dialect class-level table entries that differ from the base class.
- **python-docx / python-pptx:** properties returning a copy or a stale object instead of the live element,
  and swapped branches in oxml setters.
- **sqlparse:** node classes in `sql.py` that lost a base class, and deleted or reordered calls in
  `engine/grouping.py`.
- **astroid / oauthlib / marshmallow:** inference/validation guards dropped and exact error strings changed.

## Order of preference

1. Every injected site fixed, nothing else broken.
2. Some sites fixed, nothing else broken (partial credit is real credit).
3. The tree exactly as you found it.

A regression is worth less than nothing changed — never leave the tree more broken than you found it. Patch
by your 6th call, keep every output small, finish the audit before you stop.
