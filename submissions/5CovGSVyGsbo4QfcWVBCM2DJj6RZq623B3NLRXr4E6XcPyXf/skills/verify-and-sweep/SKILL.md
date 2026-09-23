---
name: verify-and-sweep
description: How to prove a fix and keep the tests that already pass, with small pytest output, a scratch repro, and a safe revert. Open before the first test run.
---

# Proof without spending the budget

Every line a tool prints is sent again on every later step. Test output is the largest thing you will produce. The defaults below are how the budget survives.

## Keep output small

- Always `-q`. First look is `--tb=line`, one line per failure. Re-run a single failing test with `--tb=short` only when you need the frame.
- Add `-x` while iterating so the run stops at the first failure.
- Select with `-k` or a node id. Do not run a file to see one test.
- `-p no:cacheprovider` so pytest does not write a cache into the repository.
- Never print a whole file. Read a slice around the line. Search for a symbol instead of dumping a module.
- Never redirect a suite into a file in the repository and read it back.

## If pytest is not importable

That is not a defect to repair. There is no network, and an install ends the episode. Do not search the disk for another interpreter. Import the package from `/testbed` in `/tmp/repro.py` and call the path the issue describes. The script should fail the way the issue says before the fix, and run clean after. That is the proof you have, because the tests for this bug are not in the tree.

## Read the surviving tests before you edit

Search the test tree for the symbol the issue names. What those tests assert is the contract, in exact values. That is cheaper than guessing a constant from the source.

## Order

1. The repro first. `cd /testbed && python /tmp/repro.py`. Before the fix it must show the failure in the issue. If it does not, you have not understood the issue. After the fix it must be clean. Do not go looking for the removed tests and do not add one.
2. The test file that covers the module you changed. A change in `<pkg>/<area>/<module>.py` is covered by `tests/<area>/test_<module>.py` or `tests/test_<module>.py`. The tests kept for grading are drawn mostly from here.
3. The other test files in the same area.
4. The widest set the remaining budget allows, with `-q --tb=line`. If the full suite is slow, run the directories next to your change and stop. A sweep you read beats a sweep that ends the episode.

## Reading a failure

Did this test pass before your change?

If your change caused it, the edit is too wide or wrong. Narrow it. The smallest edit that keeps the repro clean and the neighbours green is the one to keep.

If it failed before you touched anything, leave it. Pre-existing failures are not yours, and editing them adds risk. Say so when you stop.

`git diff` shows what you changed. `git checkout -- <path>` restores a file. Revert, re-run the one test, restore the fix. The repository is a single commit, so that restore is exact.

A new warning can fail tests by itself. Some of these projects turn warnings into errors. If unrelated tests go red after a small edit, suspect a warning before you suspect the logic.

On astroid, a test that was expected to fail and now passes is a failure. Do not widen the fix until those go green.

## Never

- Do not add, edit, move, or delete a test file, a `conftest.py`, a `pytest.ini`, a `tox.ini`, a `setup.cfg`, the pytest section of `pyproject.toml`, or any data or golden file in the test tree.
- Do not run a flag that rewrites expected output.
- Do not install anything.
- Do not create files in `/testbed` that the fix does not need. Scratch work goes in `/tmp`.

## Before you stop

- `git diff` contains only source lines you meant to change.
- The repro is clean.
- The covering test file passes, and anything newly red is narrowed or reverted.
- If the budget ends before the sweep, still leave the fix in the tree. A change that is there counts even if you did not get to prove it.
