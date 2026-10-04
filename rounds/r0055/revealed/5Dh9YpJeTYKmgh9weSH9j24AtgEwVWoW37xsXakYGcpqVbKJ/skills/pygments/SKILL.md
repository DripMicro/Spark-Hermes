---
name: pygments
description: Layout, test commands and known weak spots of the pygments checkout (syntax highlighter with lexers and formatters). Load when the issue imports pygments.
---
# pygments checkout

- Package at `/testbed/pygments/`: `lexer.py` (RegexLexer machinery, `bygroups`, `include`, `using`),
  `lexers/*.py` (one module per language family), `formatters/*.py`, `token.py`, `util.py`,
  `filters/`, `styles/`.
- Tests at `/testbed/tests/`; many use snapshot files of expected token streams under `tests/snippets/` and
  `tests/examplefiles/`. Never regenerate or edit them.
- Lexer damage: a state table entry reordered or missing, a regex group mapping swapped, a token type
  changed, a removed `analyse_text` heuristic. Compare with similar lexers in the same module.
- Quick check: `list(SomeLexer().get_tokens(code))` compared with the expected tokens, or
  `pygments.highlight(code, lexer, formatter)` compared with the expected text.
