---
name: sqlglot
description: Layout, test commands and an untouched source reference for the sqlglot checkout (SQL parser and transpiler). Load when the issue imports sqlglot.
---
# sqlglot checkout

## An unaltered copy of the source exists here
`/testbed/docs/sqlglot/` contains the generated API pages, and each page embeds the full module source with
line numbers, produced before the mutation. Mapping: `sqlglot/X.py` to `docs/sqlglot/X.html`, and
`sqlglot/dialects/NAME.py` to `docs/sqlglot/dialects/NAME.html` (also `optimizer/`, `executor/`).
Use it as the primary evidence:
1. Write a short script in `/tmp` that reads that one page, strips the HTML tags, unescapes the entities
   and saves plain text to `/tmp/ref.txt`.
2. `grep -n "def <function>" /tmp/ref.txt`, then print at most 60 lines of it.
3. Compare with the same function in the checkout and restore only the lines that differ in the
   functions your symptoms point at. The pages may be from a slightly newer or older release, so ignore
   unrelated drift and never paste a whole function blindly.
If the page or function is absent, fall back to the normal evidence plan.

## Layout and weak spots
- Package at `/testbed/sqlglot/`: `parser.py`, `generator.py`, `tokens.py`, `expressions.py`,
  `dialects/*.py`, `optimizer/*.py` (qualify_columns, simplify, annotate_types, ...).
- Dialects override class-level tables (`FUNCTIONS`, `TRANSFORMS`, `TOKENS` and so on) of the base
  classes; one wrong entry or a missing override is common.
- Parser methods often read a local before it is assigned after a statement was moved or deleted.
- Tests: `tests/test_*.py`, `tests/dialects/test_<dialect>.py`; `tests/fixtures/` holds expected outputs and
  must never be edited. Quick check: `sqlglot.transpile(sql, read=..., write=...)` or
  `sqlglot.parse_one(sql, read=...).sql(dialect=...)` compared with the issue's expected SQL string.
