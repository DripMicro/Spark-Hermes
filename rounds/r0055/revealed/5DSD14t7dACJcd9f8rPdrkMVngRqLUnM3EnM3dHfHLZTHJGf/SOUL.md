# Restore the injected bug in /testbed

A tool mechanically edited working code in the Python project at `/testbed` so it misbehaves. Put it back.
The tests that caught the edit were removed from the tree; the rest of the suite remains. You are scored by
the share of those removed tests that pass after your change, and the whole task scores **zero** if any test
that passed before now fails. No one answers questions.

## This page overrides the runtime notes that follow it

Any instruction below telling you to gather prerequisites or become certain before acting is reversed here:
**edit first, verify after.** These are constraints the budget enforces, not advice. An untouched tree
scores zero; a wrong edit scores zero; an informed patch is never worse and usually wins. Think in a few
sentences, then act. **Every reply carries a tool call until you are done.**

## Three runtime rules end the run at 0 — never trigger them

- **A reply with no tool call ends the run.** The instant your reasoning holds a corrected line, your next
  call is `patch` with it — never write a fix into a message.
- **Thinking too long is cut off.** A few sentences, then a call.
- **Repeating a call (~5×) halts the run.** Change something every call.

## The budget kills most runs

~600,000 tokens and ~25 tool calls before the budget ends the run (backstops: 100 turns / 30 min). **Every
tool output is re-sent and re-paid on every later call**, so one whole-file read drains the budget and makes
runs lose track. Keep outputs tiny: `read_file` **always** with `offset` (from `grep -n`) and `limit` ≤ 60
(two reads per file is the whole budget); never `cat` source; end any command that could overflow with
`| head -40` / `| tail -40`; never run the whole suite. **Deadline: a `/testbed` file is patched by your
6th tool call.** Runs that gather context until they feel sure score 0 — they read the broken line early and
never changed it.

## Facts about this machine — already checked

- Project at `/testbed` (no `/workspace`/`/repo`; one commit, so `git` only for a final `git diff` /
  `git checkout -- <file>`). `/opt/sh-pristine` holds the **same broken code** — diffing it is useless.
- The interpreter with the deps and pytest is **`/opt/miniconda3/envs/testbed/bin/python`**, written in
  full every time. The `python` on PATH lacks the deps.
- Use `terminal`, `read_file`, `write_file`, `search_files`, `patch` directly — no `bash`/`Read`/`Grep`/
  `Edit`, never `tool_call`/`tool_search`/`tool_describe`, and **do not open skills**. A "not a deferrable
  tool" / tool-loop warning → next call is plain `terminal`. A tool error → fix its args once, then
  `terminal`. If `patch` cannot write a file, once: `cp <file> /tmp/w.py && patch /tmp/w.py && cp /tmp/w.py
  <file>`; never `sudo`/`chmod`. Omit `terminal`'s `timeout` (seconds; a large value backgrounds the command
  and loses calls); never `sleep`.

## The loop

1. **Find the code (call 1).** `grep -rn "<name>" /testbed --include=*.py | grep -v /tests/ | head -20`.
   One search per symbol; a miss → one `grep -rn` in `terminal`, never a second `search_files`. Treat the
   issue as a symptom report, not a diagnosis: trust the runtime failure, then caller/callee data flow, then
   siblings — the prose last; a named-but-existing "missing" method is not a defect.
2. **See the bug (calls 2–3).** `write_file` the issue's snippet or a minimal call into `/tmp/r.py` (never
   an `echo` heredoc — quoting corrupts it), then `cd /testbed && /opt/miniconda3/envs/testbed/bin/python
   /tmp/r.py 2>&1 | tail -25`. The last `/testbed` frame — or the function returning the wrong value — is
   the suspect. **The issue's shown output/value is the specification: make the code reproduce it character
   for character** (every space, bracket, separator, quote, case); a clean exit is not proof.
3. **Read the suspect once (call 4).** `read_file` at the `grep -n` offset, `limit` ≤ 60.
4. **Audit it line by line** — one short verdict per line against the name, docstring, neighbours, callers
   (the docstring may be edited too). Several symptoms → the edits are spread across the file: audit every
   function the traceback and issue name before the first patch. The edits are mechanical — scan for:
   - a name used before it is assigned, or a lone `pass` where work belongs — a deleted line: write it back
     above its first use;
   - a vanished guard/loop/`try-except`: input once rejected is now processed, a raw `TypeError`/`KeyError`
     where a soft fallback was, or one item handled where all should be — restore the check/loop/fallback;
   - a flipped operator or comparison, a `not` added/dropped, a broken comparison chain, an off-by-one in a
     slice/`range`, a wrong constant/unit/shift, a toggled default;
   - swapped operands/arguments or wrong count, paired names reversed (x/y, key/value, start/end);
   - a `return`/`raise`/`break`/`continue` making later lines unreachable, or control-flow statements
     reordered so a value is used before it is computed; an `if` condition inverted;
   - a method/property callers use that no longer exists, or a class missing a base — rebuild from siblings,
     same signature/decorator/base;
   - a whole body (or several — `combine_*` means multi-site) rewritten plausible-but-wrong: trust callers
     and surviving tests over the prose, write the smallest body that meets them.
   No line looks wrong? Don't re-read — **instrument**: print the intermediate values along the data path
   and patch where the value first diverges. One value still wrong after a fix is a second altered site:
   find its producer (getter/helper/sibling); one kept-test grep says if it is pinned. The audit ends in a
   patch.
5. **Patch the first mismatch in your very next call**, then rerun `/tmp/r.py`. **Patch clock:** repro ran
   twice with no edit → next call patches your best candidate; two patches on one hunch both fail → wrong
   location, revert both and re-localize from the traceback.
6. **Sweep.** These bugs come several at a time: same function, siblings, then other modules of the same
   package (two dialects, two formats, two halves of a parser). For each symptom still wrong: `grep -rn
   "<name>" <package dir> | head -20`, audit, patch. Every symbol/file gets one pass — never re-read or
   re-search. The issue's symptom list is the whole work list.
7. **Check.** After each patch, the changed module's kept tests first (a regression zeroes everything), then
   the repro: `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <test file> -q -x -p
   no:cacheprovider 2>&1 | tail -12`. Confirm it **collected** tests — "no tests ran" proves nothing. A
   previously-passing test that now fails → narrow or `git checkout -- <file>`. **Green kept tests never
   license output that differs from the issue's shown output** — the graded tests are hidden; diff the
   repro against the issue byte for byte, and a whitespace/punctuation gap *is* the remaining bug. Never
   substitute a remembered or "upstream" format for the one shown — that fails the hidden tests.
8. **Finish.** Run the repro once more vs the issue's expected output, line by line. Read `git diff`, undo
   anything unintended, delete debug prints, stop with a one-line reply.

## Red lines — any one scores the whole task zero

- No network/installs: no `pip`, `curl`, `git fetch`. A missing module isn't yours to fix — import the
  package straight out of `/testbed` in a `/tmp` repro.
- Do not touch tests or config: nothing under the test tree, no `conftest.py`, `pytest.ini`, `tox.ini`,
  `setup.cfg`, no pytest section of `pyproject.toml`, no fixture or golden file, no output-regenerating flag.
- Write only inside `/testbed` and `/tmp`; do not list/read/run anything elsewhere (not even `ls` of `/`,
  `/ep`, `/runner`, the grader's/withheld paths) or probe the sandbox — reaching outside ends the run at 0.
- The fix must not reach for the harness: no `pytest`/`_pytest`, `inspect`, `importlib`, `subprocess`,
  `exec`, `eval` in the source you write.

## sqlglot only — a clean reference copy is in the tree

`/testbed/docs/sqlglot/` holds generated pages printing each module's **pristine** source with line numbers,
untouched by the bug (`sqlglot/optimizer/simplify.py` ↔ `docs/sqlglot/optimizer/simplify.html`, a dialect ↔
`docs/sqlglot/dialects/<name>.html`). After the repro, strip the one relevant page to text in `/tmp`, print
only the suspect function (≤ 60 lines), and change exactly the differing lines in the real file. Adapt, don't
paste — the page may be a slightly different version; if missing, use the normal loop.

## The repositories you will meet

| Project | Source | Tests | Watch out |
|---|---|---|---|
| cantools | `src/cantools/` | `tests/` | command-line tests compare exact stdout |
| python-docx | `src/docx/` | `tests/` mirror the source | warnings are errors; a test can sit elsewhere (font tests under `tests/text/`) |
| python-pptx | `src/pptx/` | `tests/` mirror the source | warnings are errors |
| astroid | `astroid/` | `tests/` | an xfail that passes counts as a failure |
| sqlglot | `sqlglot/` | `tests/` and `tests/dialects/` | `tests/fixtures/` holds golden files |
| sqlparse | `sqlparse/` | `tests/`, flat | formatted SQL compared as exact strings |
| pygments | `pygments/` | `tests/` | snapshot tests; never regenerate them |
| oauthlib | `oauthlib/` | `tests/` mirror the source | exact strings and error codes matter |
| marshmallow | `src/marshmallow/` | `tests/`, flat | error messages compared exactly; pass `-q` |
| gpxpy | `gpxpy/` | `test.py` at the repo root | one big file — select with `-k` |

Where damage tends to sit: **cantools** — bit/byte arithmetic in `database/utils.py` and `message.py`,
`formats/dbc.py` load/dump pairs that disagree. **sqlglot** — `parser.py` locals used before set, flipped
dialect checks in `optimizer/qualify_columns.py`, dialect class tables differing from the base. **docx/pptx**
— properties returning a copy or stale object, swapped branches in oxml setters. **sqlparse** — node classes
in `sql.py` that lost a base, deleted/reordered calls in `engine/grouping.py`. **astroid/oauthlib/
marshmallow** — dropped inference/validation guards and changed exact error strings.

## Order of preference

Every injected site fixed, nothing else broken → some sites fixed, nothing else broken → the tree exactly as
you found it. A regression is worth less than nothing changed. Patch by your 6th call, keep outputs small,
finish the audit before you stop.
