# Repository family map

Open only the section matching the tree. These are navigation hints, not code
to copy.

## SQL parsers and transpilers

Source is commonly a root package; tests are under tests, often split by
optimizer and dialect. A parser, generator, and optimizer may handle the same
construct differently. For dialect behavior, inspect the dialect method and
one comparable sibling, then the dialect test. Preserve distinct cases rather
than forcing every dialect through one generic path.

## Document and presentation generators

Public objects commonly delegate to an XML layer under a source package.
Trace the public property to its element getter or setter. Check None and
boolean states separately, plus element creation, removal, and dimensions.
Tests often mirror source areas. Some suites treat warnings as errors.

## CAN tools and command line parsers

Source may live under src. Command modules, database loaders, and C generation
are different paths; follow the issue to the correct one. Output checks can
compare exact text, line order, spacing, and generated files. Run the nearest
command or loader test with bounded output.

## Syntax highlighters

Lexer behavior may be tested through example files collected as tests.
Inspect option defaults, keyword versus builtin categories, state flags, and
the effect of set operations on repeated tokens. Avoid changing example files
or expected token snapshots.

## Static analysis libraries

Core nodes and inference helpers may be separate from library-specific
"brain" modules. Use a tiny source snippet to observe the inferred type or
fallback. Check the method's return contract and guards for recursive proxy
access. Test the nearest inference area.

## Geography and time series

Find the computation of each reported quantity. Recompute units and boundary
cases independently; confirm that related values use the same time and
distance units. Avoid assuming a single arithmetic change explains several
metrics.

## Authentication and protocol libraries

Trace the requested flow through its branch conditions, validation, rendering,
and return contract. Compare headers, body, query, exceptions, and callbacks
separately. A base validation hook can intentionally require subclass
implementation; inspect callers before adding a default behavior.

## Anything else

Use names in the issue, source definitions, and the nearest surviving tests.
Do not spend tool calls building a complete architecture map.