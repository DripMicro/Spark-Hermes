# Mechanical mutation reference

These labels describe search shapes, not a guarantee about the current bug.
Choose from observed behavior and confirm with a caller, sibling, surviving test,
or tiny repro. Several shapes can occur together.

| Shape | Search evidence | Repair check |
|---|---|---|
| Basic function edit | A changed boolean, default, argument, string, cast, decorator, return, or stub | Compare each branch with the call and result contract |
| Operator change | Units, set membership, precedence, arithmetic, or comparisons disagree | Check dimensional meaning and a nearby equivalent computation |
| Constant change | Boundary, offset, width, or sentinel differs | Probe first, last, empty, and exact boundary cases |
| Operand swap | Paired names or same-type arguments are reversed | Follow each value to its consumer by role |
| Control inversion | Condition and body disagree, or bodies are exchanged | Evaluate both branches with representative inputs |
| Statement shuffle | Use before definition, guard after use, early return, dead docstring | Restore causal order; ensure all needed paths remain reachable |
| Removed assignment | A local is read before binding, a result lacks fields, or pass replaces work | Trace every missing value from consumers and analogous path |
| Removed condition | A filter, continue, early return, or exception guard is absent | Restore only the guard justified by callers and edge inputs |
| Removed class member | Callers expect a missing method, property, or override | Match signature, decorator, return type, and sibling contract |
| Removed base | Inherited method or constructor behavior disappears | Compare related class declarations and imports |
| Multi-site file edit | Independent wrong values, flags, strings, or returns in one file | List all issue claims; verify each site separately |
| Multi-file package edit | A remaining symptom moves to an adjacent module | Trace the remaining path into the next source file |
| Whole-function rewrite | Coherent new body with changed interface, state, timeout, or edge cases | Reconstruct required behavior from callers and surviving tests |

## High-value checks

### Missing work

A vanished method may leave the class syntactically valid. Search for callers of
the missing name, inspect analogous members, and preserve decorator semantics.
A removed assignment may not leave a pass: inspect variables read before any
assignment on a branch, and fields used later but never initialized. When an
object construction disappears, infer each needed input from its consumer and
constructor signature. A missing guard can turn an expected skip into processing,
or let an empty value reach an index or attribute access.

### Plausible wrong work

For one-function edits, inspect the entire affected branch. A fix to argument
order can leave an altered condition or default in the same block. Compare
set operations by their membership effect: union, intersection, removal, and
toggle differ on repeated input. For constructed paths and URLs, verify both
the starting context and separators against the consumer; removing one bad
suffix may still leave an invalid path. For a tri-state property, test None as
well as True and False; preserving the unset state matters. Track return tuple
order and exception class alongside values.

### Rewrites

Treat a freshly polished implementation and its fresh docstring as one suspect
unit. Do not let the new explanation certify the code. Audit signature, callback
arguments, return type, mutation of queues or objects, error behavior, and all
special cases. A rewritten loop may change time accounting or retention of items
even when its happy path works. Compare with callers and surviving tests, then
replace only behavior you can justify. Avoid a wholesale rewrite of neighboring
working code.

### Several sites

After an evidenced fix, rerun the repro and map every issue symptom. Sweep the
edited function for other local mismatches, then adjacent functions and files
only when the symptom ledger or failing test points there. Exact string, output
order, format, and sentinel behavior can account for separate hidden checks.
A comment explaining an odd line may have been edited with the line.
