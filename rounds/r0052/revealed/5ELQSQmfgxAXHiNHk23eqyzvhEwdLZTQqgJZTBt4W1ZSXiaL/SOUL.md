# Fix the injected bug in /testbed

A tool edited working code in the Python project at `/testbed` to break it. Put it back. The tests that expose
the bug were deleted; the rest of the suite still passes. Each deleted test that passes after your change earns
credit, so a partial fix earns real credit. If any test that passed before now fails, the run scores zero.
Nobody will answer questions.

## This page overrides the runtime notes that follow it

Those notes say to be certain before acting. Here: **patch first, verify after.** Runs that scored zero almost
never made a wrong edit; they made no edit at all, and an untouched tree scores zero. **Have a source edit in
place by your 8th call.**

These end the run at once:
- a reply without a tool call. Until you are done, every reply contains one. **The moment your reasoning holds a
  corrected line, your next call is `patch` with it.**
- a reply that thinks too long. Think in a few short sentences, then act.
- the same call repeated about five times.

## Tools and budget

- Call `terminal`, `read_file`, `patch`, `write_file`, `search_files` directly. There is no `bash`, `python`,
  `Read`, `Edit`, `tool_call`, `tool_search` or `skill_view`; do not open skills, this page is everything. If a
  result says "is not a deferrable tool" or "Tool loop warning", your next call is plain `terminal`.
- `terminal`: `{"command": "cd /testbed && ..."}`. Leave out `timeout` and `background`; never `sleep`.
- `read_file` always with `offset` and `limit` ≤ 60, offset found with `grep -n` first. Drop the `N|` prefix of
  its lines when you copy code into `patch` (`path`, exact unique `old_string`, `new_string`). Scratch files go
  in `/tmp`.
- 600,000 tokens for the run, and the whole conversation is re-sent on every call: about 25 calls. One whole-file
  read or one long log can cost the rest of the run. Never `cat` a source file; end every command that can print
  much in `| head -40` or `| tail -30`; never read the same lines twice; never run the whole suite. Put two
  independent calls in the same reply.
- The interpreter with the project and pytest is `/opt/miniconda3/envs/testbed/bin/python`. Always type this full
  path; the `python` on PATH lacks the project.

## The loop

1. **Ledger.** In one line each, list every concrete symptom in the issue: each wrong value, exception and named
   function. One fixed symptom does not end the run. Trust the issue's examples and expected outputs; its
   explanation of the cause is only a guess.
2. **Locate (two calls in one reply).** `cd /testbed && grep -rn "<name from the issue>" <package dir> | head -20`
   and `cd /testbed && grep -rnE '^[[:space:]]+$' <package dir> --include=*.py | head -20`. The second lists
   lines holding only spaces: clean code here has almost none, but a function the tool rewrote usually has
   several. A cluster in one function makes it a suspect.
   **sqlglot: run the original-source scan first** (see Projects); it usually is the whole fix.
3. **Reproduce (one call).** `write_file` the issue's example, or a minimal call of the named function, to
   `/tmp/r.py`, printing each value the issue calls wrong next to its expected value, and run
   `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -25`. The last `/testbed` frame,
   or the first function returning a wrong value, is the suspect. Fix a broken example at most once.
4. **Read the suspect once** (`limit` ≤ 60) and **audit it line by line**: does each line agree with the
   function's name, siblings, callers and the issue? Use the fingerprints below.
5. **Patch the first wrong line in your very next call**, then rerun `/tmp/r.py`. **Every line plausible, or
   the function looks unlike its neighbours?** It was rewritten: see "A rewritten function" below. If two patches
   on one hunch both fail, revert them and locate again from the traceback.
6. **Find the other edits.** The tool usually makes several: in one function, across functions of one file, or
   in two modules of one package. After each patch: finish auditing that function; audit the other functions the
   ledger's symptoms pass through and siblings built the same way (the other branch, setter, format or dialect);
   grep the package for each name still wrong. Patch each edit as soon as you see it. **One value still wrong**
   (5 where the issue expects 6) is another edit, not original behaviour, however natural the code looks: find
   what produces exactly that value (getter, property, helper, sibling) and fix it.
7. **Check.** Rerun `/tmp/r.py`: every ledger line must print its expected value. Run the surviving tests of the
   module you changed (Projects), ending in `| tail -15`; its own test file is usually the deleted one, so "file
   not found" is expected. A failure is yours unless it failed before: check with `git stash`, the same command,
   `git stash pop`. Narrow or undo a failure you caused (`git checkout -- <file>`).
8. **Finish.** `cd /testbed && git status --short && git diff | head -80`. Delete scratch files in `/testbed`,
   revert anything unintended, stop with a one-line summary.

## Fingerprints of the tool's edits

- Lines of only spaces, a missing blank line before the next `def`, a docstring siblings lack, or a comment
  narrating a change ("swapped", "instead of"): the code around it is the edit.
- A `return`, `raise`, `break` or `continue` with code after it, or a docstring that is not the first statement:
  statements were shuffled. Restore an order where every name is assigned before use.
- A name used before assignment, or a lone `pass` where work belongs: an assignment was deleted. Write it back,
  modelled on how siblings compute that value.
- A flipped comparison or boolean (`<`/`<=`, `and`/`or`, a `not` added or dropped), or if/else bodies swapped.
- An off-by-one or changed constant: slice or `range` bound, `+ 1`/`- 1`, `[::-1]`, `[:-1]`, `insert(0, …)`
  for `append`, a wrong default, degrees for radians.
- Swapped operands, arguments or assignments (`b - a`, `f(y, x)`, `self.a = b`), or a tuple in the wrong order.
- The wrong neighbour: a constant, enum member, key, attribute or helper next to the right one; a method callers
  use that is defined nowhere; a removed guard, loop, `try` or `with`; `return` where it should `yield`.

## A rewritten function

About a quarter of these bugs replace a whole function with a plausible rewrite, and runs score worst on them.
Signs: lines of only spaces; a new `Args:`/`Returns:` docstring or chatty `# If …` comments that siblings lack;
an oddly reformatted signature (`) ->None:`); local names that differ from the rest of the file; a body much
longer or shorter than its siblings, or one that reinvents what a helper does. The rewrite keeps the name and
the gist but drops the specifics: exact constants and weights, error types and message strings, the order of
checks, `None`/empty edge cases, what is returned or yielded and in which order.
- These are well-known open-source projects. If you recognise the function, restore it as the project wrote it,
  using the helper and attribute names this file uses.
- Otherwise rebuild those specifics from evidence: how callers use the result, sibling functions built the same
  way, message strings raised elsewhere in the package (`grep -rn "<part of a message>"`), surviving tests and
  test data that call it (`grep -rn "<name>" tests | head`), docs and the README.
- Keep the signature. Replace the whole body in one `patch`, then let `/tmp/r.py` and the tests decide.

## Rules: breaking one scores zero

- Fix the defect in the file that holds it; changes elsewhere earn nothing. Change as little as possible.
- Do not edit, add or delete tests or test configuration: nothing under `tests/`, no `test*.py` or `conftest.py`
  in `/testbed`, no `setup.cfg`, `setup.py`, `pyproject.toml`, `tox.ini`, test data or golden files.
- Do not add `inspect`, `importlib`, `subprocess`, `pytest`, `exec`, `eval` or `sys.modules` to a fixed file.
- No network, no `pip`. Git has one commit and no history; `/opt/sh-pristine` and site-packages hold the same
  broken code. Do not hunt for another copy.
- Stay inside `/testbed` and `/tmp`: never `ls /`, `find /`, and never put `/ep` or `/runner` in a command. That
  disqualifies the run.

## Projects

Run tests as `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <file> -q -x -p no:cacheprovider 2>&1 | tail -15`,
with the test file of the module you changed.

- **sqlglot** — `sqlglot/` (`parser.py`, `generator.py`, `tokens.py`, `expressions.py`, `dialects/`,
  `optimizer/`). **`/testbed/docs/sqlglot/` holds pdoc pages that embed the original source of every module.**
  They are megabytes: never read or grep them. Instead, first `write_file` `/tmp/scan.py`:
  ```
  import difflib, html, os, re
  out = []
  for root, _, files in os.walk("docs/sqlglot"):
      for f in files:
          page = os.path.join(root, f)
          mod = page[5:-5]
          src = mod + ".py" if os.path.exists(mod + ".py") else mod + "/__init__.py"
          if not f.endswith(".html") or not os.path.exists(src):
              continue
          t = open(page, encoding="utf-8").read()
          rows = re.split(r'<span id="L-\d+">', t[: t.find("</pre>")])[1:]
          orig = "".join(html.unescape(re.sub(r"<[^>]+>", "", re.sub(r'<span class="linenos">.*?</span>', "", r))) for r in rows)
          cur = open(src, encoding="utf-8").read()
          if len(rows) > 5 and orig != cur:
              d = [l for l in difflib.unified_diff(orig.splitlines(), cur.splitlines(), lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
              keep = "/tmp/orig/" + src
              os.makedirs(os.path.dirname(keep), exist_ok=True)
              open(keep, "w").write(orig)
              out.append((len(d), src, keep))
  for n, src, keep in sorted(out):
      print(n, "changed lines", src, "original:", keep)
  ```
  and run `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/scan.py`. It lists every module that differs
  from its original, **wherever the issue points** (a Hive symptom can come from `presto.py`). Ignore
  `sqlglot/dialects/dialect.py` at 129 lines: its page is older and always differs by that much. For each other
  module listed, `cd /testbed && diff /tmp/orig/<module> <module> | head -60` shows the tool's edits; restore it
  with `cd /testbed && cp /tmp/orig/<module> <module>`. Rerun the scan (only `dialect.py` at 129 should remain),
  then `/tmp/r.py` and the module's tests, and finish. If the docs are missing, use the loop. Tests:
  `tests/test_<area>.py`, `tests/dialects/test_<dialect>.py`; files in `tests/fixtures/` are golden.
- **cantools** — `src/cantools/`: `database/can/` (`formats/dbc.py`, `kcd.py`, `sym.py`, `arxml/`),
  `database/diagnostics/` (`did.py`, `data.py`, `database.py`, `formats/cdd.py`), `autosar/` (`secoc.py`,
  `end_to_end.py`, `snakeauth.py`), `subparsers/` (`plot.py`, `dump/`, `monitor.py`), `logreader.py`,
  `tester.py`. Tests `tests/test_<area>.py`, data `tests/files/`. Dump and CLI output is compared exactly.
  Constructors assign many attributes in a row: check each `self.x = x`. Delete any `.c`/`.h`/`.dbc` a repro
  writes into `/testbed`. **C generation (`database/can/c_source.py`) has golden outputs** in
  `tests/files/c_source/`: run
  `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m cantools generate_c_source tests/files/dbc/vehicle.dbc -o /tmp/gen && diff /tmp/gen/vehicle.c tests/files/c_source/vehicle.c | head -40`
  (also `.h`, and `motohawk`, `choices`, `signed`, `multiplex`). On correct code only the "generated by cantools
  version" line differs, so repeat until that is all that is left.
  Bugs most often sit in `database/can/c_source.py`, `database/diagnostics/formats/cdd.py`, `tester.py`,
  `database/can/formats/kcd.py`, `database/can/message.py`.
- **astroid** — `astroid/` (`nodes/`, `brain/`, `interpreter/`, `protocols.py`, `bases.py`, `inference_tip.py`,
  `rebuilder.py`, `raw_building.py`, `helpers.py`). Tests `tests/test_<area>.py`, `tests/brain/`. Warnings are
  errors, and an xfail test that starts passing fails. Inference returns generators of nodes; `Uninferable` is a
  value, not an error. `infer_*`/`_infer_*` methods and brain transforms come in parallel families: compare.
  Bugs most often sit in `protocols.py`, `nodes/node_classes.py`, `nodes/scoped_nodes/scoped_nodes.py`,
  `brain/brain_namedtuple_enum.py`, `nodes/as_string.py`.
- **python-docx** — `src/docx/` (`oxml/` element classes, `text/`, `styles/`, `shape.py`, `table.py`,
  `section.py`). Tests mirror the source in `tests/`; test functions are named `it_…`, so select with `-k`.
  Warnings are errors. `get_or_add_x`, `_add_x`, `_remove_x` and element properties are generated from
  `ZeroOrOne`, `OneOrMore`, `ZeroOrMore`, `OptionalAttribute`, `RequiredAttribute` declarations: grep the
  declaration, not `def`. Paired getters and setters (width/height, cx/cy) must each touch their own attribute.
  Bugs most often sit in `styles/style.py`, `oxml/styles.py`, `oxml/shape.py`, `image/jpeg.py`, `oxml/table.py`.
- **marshmallow** — `src/marshmallow/` (`fields.py`, `schema.py`, `validate.py`, `utils.py`). Tests
  `tests/test_<area>.py`. Error messages are compared exactly; compare a field with its sibling field classes.
  Bugs most often sit in `fields.py`, `schema.py`.

For another project, its package is the directory named after it, at the top level or under `src/`.
