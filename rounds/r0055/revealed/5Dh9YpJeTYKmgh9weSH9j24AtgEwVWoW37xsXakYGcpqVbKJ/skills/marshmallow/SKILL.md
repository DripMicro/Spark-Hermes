---
name: marshmallow
description: Layout, test commands and known weak spots of the marshmallow checkout (object serialization and validation). Load when the issue imports marshmallow.
---
# marshmallow checkout

- Source under `/testbed/src/marshmallow/`: `fields.py`, `schema.py`, `validate.py`, `utils.py`,
  `decorators.py`, `error_store.py`. Tests flat in `/testbed/tests/`.
- Error messages are compared exactly, including punctuation and the placeholders filled in from
  `default_error_messages`; a reworded or wrongly formatted message is a frequent change.
- Field logic splits into `_serialize` and `_deserialize` pairs; one side altered makes a round trip
  fail. Options such as `allow_none`, `required`, `load_default`, `dump_default`, `data_key`, `only`,
  `exclude`, `partial` and `many` each have a guard; check that the guard still exists and has the right
  sense.
- Validators in `validate.py` share a pattern (`_repr_args`, `_format_error`, `__call__` raising
  `ValidationError`): compare the suspect with its siblings.
- Run tests with `-q` (the suite is large) and select by file.
