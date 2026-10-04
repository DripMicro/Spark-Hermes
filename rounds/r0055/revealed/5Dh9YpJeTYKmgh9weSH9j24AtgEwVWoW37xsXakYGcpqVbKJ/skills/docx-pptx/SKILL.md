---
name: docx-pptx
description: Layout, test commands and known weak spots of the python-docx and python-pptx checkouts (Office Open XML document libraries). Load when the issue imports docx or pptx.
---
# python-docx / python-pptx checkouts

- Source is under `/testbed/src/docx/` or `/testbed/src/pptx/` (not directly under `/testbed`). Tests live
  in `/testbed/tests/`, mostly mirroring the source tree, but some sit elsewhere (font behaviour is tested
  under `tests/text/`, for example). There is also an acceptance suite under `features/`; leave it alone.
- Layers: `oxml/` holds element classes built from declarative descriptors (`ZeroOrOne`, `OneAndOnlyOne`,
  `OptionalAttribute`, `RequiredAttribute`); proxy objects in `text/`, `table.py`, `section.py`,
  `shape*`, `parts/`, `opc/` wrap them. Damage often sits in a property getter or setter: returning a new
  or copied element instead of the live one, an inverted `None` check, swapped branches when a value is
  cleared, wrong unit conversion (EMU, twips, points via `shared.py` `Length` helpers).
- `opc/` (package reading and writing): unmarshalling order, relationship lookups by `rId`, partname
  handling. When code calls a method that is missing, check whether a similarly named method exists on
  the same class before recreating one; the call may have been the line that changed.
- Warnings are configured as errors in the test run, so a restoration must not emit any new warning.
- Quick check: build a document in memory (`docx.Document()` / `pptx.Presentation()`), exercise the
  property from the issue, and assert the value; `tests/test_files/` holds sample documents if needed.
