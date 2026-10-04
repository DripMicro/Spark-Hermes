---
name: sqlparse
description: Layout, test commands and known weak spots of the sqlparse checkout (non-validating SQL tokenizer, grouper and formatter). Load when the issue imports sqlparse.
---
# sqlparse checkout

- Package at `/testbed/sqlparse/`: `lexer.py` and `keywords.py` (token rules), `sql.py` (token and group
  classes such as `Identifier`, `Function`, `Parenthesis`, `Where`, `Case`), `engine/grouping.py` (the
  passes that build groups), `engine/statement_splitter.py`, `filters/` (reindent, aligned indent,
  others), `formatter.py`.
- Tests at `/testbed/tests/`, flat (`test_grouping.py`, `test_format.py`, `test_regressions.py`,
  `test_tokenize.py`, `test_parse.py`).
- Grouping passes run in a fixed order inside one driver function; a pass deleted or moved changes
  results everywhere. Group classes rely on their base classes for behaviour, so a class that lost a base
  class or a method fails in many places at once.
- Formatter output is compared as exact strings including newlines and indentation width. Put the expected
  text in a triple-quoted string in your check and compare with `==`.
- Quick check: `sqlparse.parse(sql)[0].tokens`, `._pprint_tree()`, or `sqlparse.format(sql, reindent=True)`.
