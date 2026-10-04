---
name: astroid
description: Layout, test commands and known weak spots of the astroid checkout (the static inference library behind pylint). Load when the issue imports astroid.
---
# astroid checkout

- Package lives directly at `/testbed/astroid/`; tests at `/testbed/tests/` (plus `tests/brain/` for the
  per-library inference plugins and `tests/testdata/` for sample modules).
- Modules are very large: `nodes/node_classes.py`, `nodes/scoped_nodes/`, `protocols.py`, `inference.py`,
  `bases.py`, `brain/brain_*.py`, `modutils.py`, `rebuilder.py`, `nodes/as_string.py`. Always `grep -n` the
  definition first and view 40 lines around it.
- Typical issue shape: a snippet that builds a tree with `astroid.extract_node(...)` or `astroid.parse(...)`
  and calls `.infer()`, `.as_string()`, `.lookup()`, `.mro()` or `.getattr()`. Turn the expected inferred
  value or rendered string into the assertion of your check script.
- Inference functions are generators: a deleted `yield`, a `return` where `yield` belongs, or a missing
  `raise InferenceError` / `Uninferable` fallback are frequent damage. Compare with neighbouring
  `infer_*` / `_infer_*` functions, which follow one shared pattern.
- `as_string` visitors (`visit_*` in `nodes/as_string.py`) have many near-identical siblings: a
  formatting difference from the siblings is usually the altered line.
- Context objects (`InferenceContext`, `context.clone()`, `copy_context`) are passed along on purpose; a
  dropped or swapped context argument is a common subtle change.
- Some changes are reverts of a real upstream pull request touching several functions: expect more than
  one site and read the issue's whole symptom list.
- Running tests: `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest tests/<file> -q -x -p no:cacheprovider 2>&1 | tail -15`.
  Strict xfail is on: a test marked xfail that starts passing counts as a failure, so do not "fix" more
  than the issue describes.
