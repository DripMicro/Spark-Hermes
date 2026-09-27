# Objective

Fix the injected defect(s) in product source under /testbed.
A source edit is required. Partial credit matters: keep an improving repair unless it causes a regression.

# Priority

1. Identify the repository and use only the matching round rule below.
2. Locate the smallest suspect source block from the failing behavior or test.
3. Patch as soon as local evidence supports a plausible mismatch.
4. Verify immediately with the smallest relevant reproduction or existing test.
5. Keep useful partial repairs and continue only for explicit unresolved symptoms.
6. Stop when the requested behavior works and git diff is clean.

Make the first source edit by call 7 when a plausible mismatch is visible.
If no source edit has happened by call 15, stop broad investigation and patch the strongest locally-supported candidate.
Do not wait for certainty before trying a small informed repair.

# R24 repository rules

Use these as navigation priors, not as assumed answers. If the hidden bug is in a different subsystem, use the generic priority loop.

## cantools

Two hidden tasks come from cantools.

ARXML/database symptom:
- trace loader/parser assignment -> stored private attribute -> public property;
- compare nearby getters/setters and sibling properties;
- if several properties are wrong, inspect the same bounded class or loader path for multiple mutations.

Monitor/CLI state symptom:
- trace input handler -> state mutation -> rendering;
- compare opposite operations such as up/down or page-up/page-down;
- check page index, bounds/clamping, and refresh/modified state.

Generated/parsed CAN value symptom:
- determine whether the wrong value appears during loading, model storage, or output transformation before patching.

## marshmallow

Start with the concrete Field subclass in `src/marshmallow/fields.py`.
For serialization/deserialization, compare serialize vs deserialize and track the exact input/output shape.
Distinguish name lookup vs value lookup and scalar vs collection paths.
Invalid input should follow the existing `ValidationError` path, not be returned as an error object.

## astroid

Use the failing test to find the real output path; do not trust the issue's named method blindly.
For representation/formatting bugs, inspect `NodeNG`, the actual visitor/formatter, field metadata, and operator/precedence handling.
Patch the smallest proven field-order, metadata, precedence, or formatting mismatch.

## oauthlib

Trace one request through the existing local pipeline.
For OAuth1 validation, inspect request construction/parameter extraction, duplicate detection, validator results, then signature verification.
Preserve form-urlencoded vs non-form body handling.
Check that final validity actually combines the relevant boolean checks.
For missing/swapped values, inspect argument and object wiring before searching broadly.

## sqlparse

For statement splitting, start in `sqlparse/engine/statement_splitter.py`.
Treat splitting as a state machine: inspect nesting level and BEGIN/END/CASE/IF/FOR/WHILE transitions.
Compare each increment with its matching decrement and trace the exact token that causes an early split.
Patch `_change_splitlevel` or the directly proven split condition before unrelated grouping/parser code.

# Generic repair rules

The issue's diagnosis may be wrong; its observable requested behavior is the target.
Prefer concrete runtime/test behavior and local code contracts over issue prose or remembered upstream source.

Read only the suspect function/block plus one directly useful caller, sibling, or test when needed.
Reproduce only when runtime output can locate the failing branch or distinguish plausible repairs.
If the issue plus local source already exposes the mismatch, patch immediately.

Make the smallest product-source change that restores the local contract.
Do not refactor unrelated code.
Preserve working signatures, argument meaning, return shape, exception behavior, normalization, and state conventions unless they are the defect.

If one bounded read exposes several obvious independent mutations in the same contract, repair them together.
If verification improves, keep the useful repair and continue with remaining explicit symptoms.
If your change introduces a regression, revise or revert that disproved part.
If verification itself is broken, use a closer verification instead of rejecting a locally-supported patch.

Before stopping, inspect the edited block once for another obvious same-contract defect and inspect git diff.

# Tools

Project interpreter: `/opt/miniconda3/envs/testbed/bin/python`

Use direct tools directly: `terminal`, `read_file`, `search_files`, `patch`, `write_file`.
Never route them through `tool_call`, `tool_search`, or `tool_describe`.
If a direct tool call fails, correct it once; if that route still fails, use a simple bounded terminal command.
Never repeat an identical failed call.

Keep reads, searches, and command output small.
Run focused existing tests, not a large whole-suite test for reassurance.
Confirm the intended tests were collected.

# Boundaries

Modify only product source inside /testbed. Scratch files belong under /tmp.
Do not modify/add tests, fixtures, snapshots, golden/test data, grader files, configuration, packaging, dependency files, import machinery, or agent settings.
No network, package installation, git history, alternate checkout, pristine-source comparison, or hidden grader/runner/withheld inspection.
Never wait for human input.

# Finish

Leave only justified product-source edits in git diff.
Do not spend remaining calls re-proving a working repair.
