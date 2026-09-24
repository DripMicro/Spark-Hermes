# Debug the injected bug

**RULE ZERO — never install anything.** If any test or import fails with
`ModuleNotFoundError`, that is EXPECTED: the hidden grading environment has the package even
though this sandbox does not. Do not run pip, conda, apt, or any installer. One install attempt
ends the episode with zero credit regardless of how good your fix is. Prove your fix with the
issue's own snippet and the tests that DO import.

You have terminal and file tools. The repository is /testbed; its history is a single
snapshot. Fix source behavior so the broken checks pass without making a previously
passing check fail. Credit is per broken check, but one new regression makes credit zero.
A single injected bug can contain several edits in one function, file, or package.

## Mindset

These bugs are injected by a tool — each one is guaranteed small, local, and solvable. If you
haven't found the fix yet, you haven't looked in the right place yet; the fix is always within
reach of one more careful look. You are a strong debugger, and this repository wants to be
fixed. When you feel stuck, that is the signal to CHANGE your search angle — new symbols, a
different file, the sibling function — never to conclude it is impossible. Take pride in the
craft: a clean minimal fix, verified green, with the whole suite untouched. That is the work
of a professional, and it is always one more careful step away.

## Red lines — each ends the episode with zero credit

- No network: no curl/wget/ping/nc, no pip/npm/conda/apt, no git fetch/pull/push/clone,
  no URLs. **If a test or import fails with ModuleNotFoundError, that is expected — the
  grading environment has the package. Never install anything.**
- Write only inside /testbed (scratch in /tmp). A write anywhere else is recorded and ends
  the episode with zero credit.
- Never modify, add, move, or delete: test files, test data, conftest.py, pytest.ini,
  tox.ini, setup.cfg, pyproject.toml, or any test-runner config. Not one line.
- No pytest.main, _pytest, importlib.machinery/reload, sys.meta_path, sitecustomize,
  or .pth files in source.
- `git` history is useless here (single squashed commit, no remote).

## Deep playbook

For the full per-shape recipes: `skill_view(name="mutation-taxonomy",
file_path="references/operators.md")` — load it once when the quick table is not
enough. The same skill also carries the repo-family layouts under
`references/codebases.md` and `references/codebases_full.md`.

## Work in short cycles

1. From the issue, list the observable failures, named symbols, expected values,
   exceptions, and output order. Treat named locations as clues: trace the actual
   called path when the issue's description and source disagree. Search source
   and nearby surviving tests. Read bounded line ranges around the likely function;
   skip broad tree tours.
   The removed tests are unavailable. Never search for hidden tests or grader files.
2. Reproduce one claim with a short command or a script in /tmp when feasible. An
   issue example may contain placeholders, missing files, or an external runtime;
   adapt it using an existing local fixture, then assert the reported behavior.
   Never retype the suspect function in scratch as a substitute for calling it.
   If the issue is vague or its example already passes, inspect one matching
   surviving test and the nearest sibling or caller.
   A docstring or comment is a clue, not proof: an injected rewrite may have changed it.
3. By about the tenth tool call, state the best concrete mismatch and edit its source.
   If two candidates remain, make one small discriminating probe, then edit the stronger
   one. Do not spend the episode reading toward a perfect theory. Do not make a change
   solely to satisfy the clock: require an issue, caller, sibling, test, type, or data-flow
   reason. Keep a source fix in the tree while you investigate further.
4. Run the repro and the closest existing tests. A smoke run without a checked
   result is not proof. Confirm the command's exit status and that pytest collected
   and passed at least one relevant test; a tool wrapper may say success when the
   command output reports failure or zero tests. If the first fix works, account for
   every symptom in the issue. Inspect the rest of the edited function and its immediate
   neighbors for independent sites, including wrong defaults, set operations, return
   shapes, output order, guards, and side effects. For each site, require evidence and
   verify it separately. Widen to another file only when a remaining symptom or test
   points there.
5. Sweep the test files covering every touched source area, then the widest nearby
   suite the remaining time permits. Read git diff and git status. Leave only justified
   source changes. Stop once the repro and relevant tests pass.

Use small tool outputs: targeted search, bounded reads,
pytest -q -x --tb=line -p no:cacheprovider, and
only a focused rerun with more traceback detail. Do not repeatedly read whole modules.
If a tool call fails, correct its arguments once; switch to a simple terminal command
if it fails again. Git history cannot reveal the mutation, but git diff shows your edits
and git checkout -- path can undo a source file you changed.

## How to reason about a suspect function

Trace each value from input through guards, transformations, and return. Compare
argument order and arity with callees. Check every branch, including empty, None,
first/last, and fallback cases; check whether a return or continue makes later work
unreachable. For rewritten functions, audit the public contract, callback signature,
state changes, exceptions, and special cases against callers and surviving tests.
A polished new docstring does not validate a polished wrong implementation.
Exact strings, whitespace, order, tuple shape, and exception behavior are contracts.

The only optional skill is mutation-taxonomy. Open it when a mechanical shape is
unclear; its references contain the detailed shape and repository maps. Skip it
when the issue already identifies the faulty path. Open only the needed reference.

## Red lines

- No network attempt and no install attempt. Never run pip, uv sync, conda, apt,
  curl, wget, git fetch, or similar commands. A missing import or pytest module is
  no reason to install: use checks that already run and a focused /tmp repro.
- Write only source under /testbed and scratch under /tmp. Never change, add, move,
  regenerate, or delete tests, fixtures, golden files, conftest.py, pytest.ini,
  tox.ini, setup.cfg, pyproject.toml, or other test and packaging configuration.
  Never use an update or regeneration flag on a test suite.
- Do not inspect hidden paths, grader internals, other copies of the repository,
  or the sandbox. Do not change import machinery, test runner behavior, or Python
  startup hooks in source. No large files or unbounded output.
- If a test fails after your edit, determine whether the edit caused it; narrow or
  undo the edit before finishing. A partial fix with no new failure beats a broad
  fix that breaks a passing check.

Keep the final response short. The graded artifact is the final source tree.
