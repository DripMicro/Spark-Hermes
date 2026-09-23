# Fix the injected bugs, and do not break what already passes

`/testbed` is a Python project with one or more small edits injected into working source. Make the tests those edits broke pass again. Credit is the share of those tests you restore. If any test that passed before your edit now fails, the task scores zero. A partial fix that leaves the rest of the suite green is worth real credit. A regression is worth less than leaving the tree untouched.

## What this sandbox actually allows

The tests written for this bug were removed from the tree. Do not search for them and do not add one. A short script in `/tmp` is how you reproduce the issue. The other tests are still there. Grep them for the symbols the issue names: they state the contract in exact values.

You have a token budget, not a hundred free turns. The whole conversation is sent again on every step, so a large tool result is paid for on every step after it. Plan on about thirty steps. Read slices, not whole files. Run tests quietly. Open at most one skill, and only the one you need next. Opening all of them spends a large part of the budget before you have read the code.

A task usually contains more than one injected edit, often in the same file, and they are independent. Several symptoms or several named symbols means several sites. Fixing the first one is not finishing.

## The loop

Orient from the issue, not by browsing. Take the symbols it names and search for them. `codebase-map` has the layout, the test command, and the traps for the repository you are in. Open it once you know which tree `ls /testbed` shows, then do not open it again.

Reproduce before you theorize. Put the issue's snippet in `/tmp/repro.py` and run it from `/testbed`. The traceback names the file and the line. If there is no snippet, call the named function yourself.

Localize by disagreement. An injected line conflicts with the docstring, the type hints, a sibling that does the same job, or its own callers. `bug-shapes` lists the forms these edits take. Open it after the repro, before you edit.

Edit by step ten even if you are unsure. The usual zero is an episode that reads until the budget ends and never changes the tree. Apply the best candidate you have and keep going from there. `git diff` and `git checkout -- <path>` make a wrong edit cheap to undo. Another file opened "to be sure" is how the budget dies.

Do not re-read a function you have already seen. Do not follow a base class into machinery the issue did not ask you to change.

Change the smallest span you can justify. No rename, no reformat, no cleanup. Do not "fix" a neighbouring line because it looks uneven. If you cannot say what is wrong with it, leave it.

Then look for the other sites. Re-read the file you edited, every function, and ask whether each symptom in the issue now has a cause. If the issue named several things and you changed one, continue.

Sweep, then stop. Run the test file that covers the module you changed, then the widest set you can still afford, quietly. `verify-and-sweep` has the commands. A new failure means narrow the edit or revert it before you finish.

A plausible fix that is in the tree beats a perfect diagnosis that is not. Leave enough budget to run the covering tests.

## Undo

This git history is one commit and no remote. It does not explain the bug. It does undo. `git diff` is the exact list of what you changed. `git checkout -- <path>` restores a file. Read `git diff` before you stop and put back anything you did not mean to change.

## These end the task at zero

- No network. No installs, no fetching, no cloning. One packet leaving the sandbox ends the episode.
- A missing tool is not a problem to solve. If pytest is not importable, do not search the disk for another interpreter and do not try to install one. Import the package from `/testbed` in a `/tmp` script and call the path the issue describes.
- This tree is the only source. Other copies of the library may exist on the machine. Do not look for one and do not diff against one. The docstring, the siblings, and the surviving tests are the evidence, and they are inside `/testbed`.
- Do not touch tests or their configuration. Nothing under the test directory, no test module, no `conftest.py`, no `pytest.ini`, no `tox.ini`, no `setup.cfg`, no pytest section of `pyproject.toml`, no fixture or golden file. Not to edit, move, or regenerate.
- Never run a flag that rewrites a suite's expected output. That rewrites the tests.
- Write only under `/testbed` and `/tmp`. Do not browse the filesystem root and do not look for how grading works.
- Do not import the test runner from project source, do not reload modules to hide a change, and do not patch import machinery. Fix the code the issue is about.
- Do not fill the disk.

## Order

1. Every injected site fixed, and nothing that passed before now fails.
2. Some sites fixed, and nothing that passed before now fails.
3. The tree exactly as you found it.

Never leave the repository more broken than you found it.
