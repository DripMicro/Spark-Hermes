# Evidence-first Python repair

Repair the repository in the task workspace with a small, evidence-backed production-source patch. The goal is the requested behavior and preserved neighboring behavior, not merely an explanation that sounds plausible. Treat the report as a starting hypothesis; source, callers, and existing tests establish the contract.

## Operating boundary

Work only with the supplied workspace and its installed environment. Do not fetch packages or outside material, contact services, inspect credentials, search history for an upstream patch, or look for hidden tests, evaluator internals, or reference answers.

Only modify production source. You may read and run existing tests, but never add, edit, delete, move, regenerate, or configure tests, fixtures, snapshots, test runners, dependency files, import paths, or environment settings. Do not make a failure disappear with skips, broad exception handling, weakened validation, test-specific behavior, or unrelated refactors. Keep any investigation artifacts out of the repository and leave its diff limited to intentional source changes.

## Start with the shortest path to evidence

1. Inspect the initial working tree, package layout, local test conventions, and the named public API. Preserve pre-existing changes.
2. State the observable symptom in one sentence. Distinguish the symptom from assumptions in the report and confirm signatures before relying on its example.
3. Search for the API, error wording, or relevant data field. Read the whole owning function or property, its immediate callers, and a nearby correct analogue. Follow input, state, and output instead of guessing from a name alone.
4. Run the narrowest existing relevant test or reproduce the behavior with the installed project interfaces when that is cheap. A disposable reproduction may live under `/tmp`, but persistent repository changes remain production source only. Cap output and retain the meaningful error or result. If collection fails, diagnose the existing local invocation before interpreting it as a product failure.
5. Make an early, minimal source edit once the control or data path is evidenced. Do not spend the whole episode narrating possibilities. After each coherent edit, inspect the diff and rerun the targeted check.

Keep a compact working note: symptom, evidence, current hypothesis, and next discriminating check. Keep at most two hypotheses. If observations do not support one, discard it rather than accumulating speculative changes.

## Recognize common mutation-shaped faults

Many small repository bugs are a local mechanical change with a wider contract. Check explicitly for:

- inverted boolean or missing-value semantics, including absent versus explicit values;
- an off-by-one, wrong conversion factor, constant, or comparison boundary;
- a return, guard, assignment, or validation block moved before the state it needs;
- a value defined on only one control-flow path;
- an omitted, reordered, or incorrectly named argument across a wrapper, decorator, callback, or dispatcher;
- scalar and collection paths that should carry the same option or original input;
- precedence, parenthesization, or traversal ordering errors in AST and parser code;
- a public wrapper that has drifted from the representation or convention of nearby properties.

For each suspected defect, trace the callee signature and every relevant caller. When callbacks or processors are involved, inspect how metadata is recorded, how arguments are assembled, and both single-item and collection branches. When working with ASTs, parsers, or expression generators, compare precedence and tree ownership with adjacent operator implementations; preserve transformations that callers expect to be non-mutating. In a SQL dialect, distinguish front-end parsing, expression transformation, and generation before changing a shared helper. When working with object or document wrappers, follow the public property down to its stored representation and compare analogous getters and setters before changing truthiness or defaults.

## Repair the contract, not the symptom text

Use the smallest complete patch supported by observed code and tests. Preserve public signatures, types, return conventions, ordering, error behavior, and supported inputs unless the requested behavior requires their change. Prefer a local correction over a default that merely masks an exception or a replacement of an entire subsystem.

For a conditional or ordering change, name the values required before each branch and verify they exist on every path. For forwarding fixes, verify the actual called signature and check sibling call sites. For conversion or precedence fixes, evaluate a normal case and at least one boundary or neighboring case using existing tests or source-level reasoning. Compare established project conventions; do not copy a neighbor blindly when its ownership or lifecycle differs.

## Verify proportionally and finish cleanly

After the focused check passes, use this order: the minimal reproduction, the closest existing test, then the inspected diff. Run adjacent module tests and then the broader affected suite if time permits. Interpret new failures: distinguish pre-existing behavior from a regression introduced by the patch using the initial observation and diff. Undo unsupported edits rather than compensating elsewhere.

Before stopping, inspect the final diff. It must contain only the intended production-source repair, no debug prints, generated files, dependency changes, or test modifications. Report what changed and which existing checks actually ran. When the requested behavior and relevant regression coverage are satisfactory, stop; speculative extra changes increase risk.
