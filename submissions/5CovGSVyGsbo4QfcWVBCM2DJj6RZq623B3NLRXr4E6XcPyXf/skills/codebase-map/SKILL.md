---
name: codebase-map
description: Layout, test command, and the traps that zero a task, for astroid, cantools, and python-docx. Open once, after ls /testbed tells you which repository you are in, and before the first test run.
---

# Which repository

`ls /testbed` is enough. Read the matching section only.

Two facts to pin down before editing: where the module named in the issue lives, and which test file covers it. The tests kept for grading are drawn mostly from the file that covers the code you change.

## astroid

Source is the top-level `astroid/` package. Tests are `tests/`, mostly flat, plus `tests/brain/` and `tests/testdata/`.

This is an AST and inference library. The parts that matter: `nodes/` (`node_classes.py`, `scoped_nodes/`, `node_ng.py`, `as_string.py`), `brain/` with one module per third-party library it models, `builder.py` and `rebuilder.py`, `bases.py`, `protocols.py`, `inference_tip.py`, `manager.py`, `modutils.py`, `helpers.py`, `objects.py`, `arguments.py`.

Inference is generator-based. `infer()` and `_infer()` yield results, and they yield an uninferable sentinel when they cannot decide. A `yield` turned into a `return`, a dropped sentinel branch, or a reversed generator order looks locally coherent and fails many tests. Node classes list their children in field tuples; compare a node with the siblings in the same file. String forms of nodes live in `as_string.py` and must match what the tests print, character for character.

Two traps, and either one zeros the task. Pytest is configured to treat warnings as errors, so a new warning fails tests that have nothing to do with your edit. Expected-failure tests are strict: a test marked as expected to fail that starts passing is itself a failure. Fix only what the issue asks. Do not "improve" nearby inference.

Tests: `python -m pytest tests/test_inference.py -q --tb=line`, or the file for the area you touched. Use `-k` while iterating. `tests/test_nodes.py` and `tests/test_scoped_nodes.py` are the other usual homes.

## cantools

Source is `src/cantools/`. Tests are `tests/`, with sample databases in `tests/files/`. Those files are fixtures. Never edit them.

The parts: `database/can/` (`database.py`, `message.py`, `signal.py`, `node.py`, `bus.py`) and `database/can/formats/` (`dbc.py`, `kcd.py`, `sym.py`, `arxml/`). The command line is `subparsers/` (`list.py`, `dump/`, `decode.py`, `convert.py`, `plot.py`, `monitor.py`, `generate_c_source.py`).

The subcommands print. Their tests compare exact stdout, so a wrong column order, a changed case, or an extra space is the bug, not a close approximation. Generated C is the same kind of contract: names, order, and separators have to match. A `None` that reaches a division in a parser is usually a field the format module stopped filling; compare that parser with the sibling format that still fills it.

`tox.ini` adds verbose pytest options. Pass `-q` yourself or the run will print more than you can afford.

Tests: `python -m pytest tests/test_database.py -q --tb=line -k <name>` while iterating, then the file. Also `tests/test_command_line.py`, `tests/test_convert.py`, and `tests/test_list.py` when the issue is about printing or converting.

## python-docx

Source is `src/docx/`. Tests are `tests/`, mirroring the package (`tests/text/`, `tests/oxml/`, `tests/parts/`). `features/` is not pytest. Ignore it.

Public objects live in `document.py`, `table.py`, `text/paragraph.py`, `text/run.py`, `section.py`, `shape.py`. The XML layer is `oxml/`, with element classes built from the descriptors in `oxml/xmlchemy.py` and value types in `oxml/simpletypes.py`. Packaging is `opc/` and `parts/`.

A public method usually forwards to a `CT_*` element. If the public method looks right, the bug is one level down, in `oxml/`. Image collections and paragraph breaks are package and text behaviour; follow the call into the element class before you edit the public wrapper.

The main way to score zero here: pytest treats warnings as errors. A new warning fails unrelated tests. Do not introduce one and do not silence one.

Tests: `python -m pytest tests/text/test_paragraph.py -q --tb=line`, or the mirrored path for the module you changed.

## If the tree is none of these

Source is either a top-level package or under `src/`. Tests mirror it under `tests/`. Golden files and fixtures live in the test tree and are never edited. Run the test file whose name matches the module you changed.
