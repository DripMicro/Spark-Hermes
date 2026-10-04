---
name: cantools
description: Layout, test commands and known weak spots of the cantools checkout (CAN bus database parsing, encoding and command-line tools). Load when the issue imports cantools.
---
# cantools checkout

- Source is under `/testbed/src/cantools/` (not `/testbed/cantools/`). Tests in `/testbed/tests/`, sample
  database files in `/testbed/tests/files/` (dbc, kcd, sym, arxml, cdd).
- Hot spots: `database/utils.py` (start-bit and byte-order arithmetic, formatting helpers),
  `database/can/message.py` and `database/can/signal.py` (encode/decode, choices, scaling, multiplexing),
  `database/conversion.py`, `database/can/formats/` (dbc, kcd, sym, arxml readers and writers),
  `database/diagnostics/`, and `subparsers/` (decode, dump, list, monitor command output).
- Format modules come in load/dump pairs: if loading and dumping disagree, one side was altered. A
  round-trip (load a file from `tests/files/`, dump it, load it again) is a fast check.
- Arithmetic damage is often one character: a shift amount, a mask, `//` against `/`, a little-endian
  branch handled like big-endian, an off-by-one in a bit range. Recompute one value by hand.
- Command-line output is compared character for character, including spaces and brackets. Copy the
  issue's expected line literally into your assertion.
- Test files: `test_database.py`, `test_command_line.py`, `test_dump.py`, `test_list.py`,
  `test_tester.py`, `test_conversion.py`, `test_diagnostics_database.py`, `test_monitor.py` and others;
  grep them for the function name before choosing which to run.
