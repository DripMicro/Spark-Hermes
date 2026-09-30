# Fix the production defect(s) in /testbed

Keep every explicit symptom in the issue in mind and repair the production source without breaking behavior that already works.

## Loop

LEDGER -> REPRODUCE -> AUDIT -> PATCH -> VERIFY -> LOCAL SWEEP -> NEXT SYMPTOM -> STOP

### 1. LEDGER
Track every independent concrete symptom or required behavior from the issue.
Do not discard another symptom just because the first one is fixed.

Treat the issue's diagnosis as a hypothesis.
Prefer observed behavior, caller/callee data flow, and the local contract over the prose.

### 2. REPRODUCE / LOCATE
Work in /testbed.

Search narrowly for the named symbol, traceback location, wrong value, or entry point.

Use one minimal reproduction or focused existing test when it can distinguish the broken behavior from the expected behavior quickly.

Read the suspect function or block and only the nearby code needed to understand its contract.

### 3. AUDIT
Before patching, inspect the suspect function for concrete corruption:

- missing assignment, guard, loop, or handler
- inverted condition or branch
- swapped arguments, operands, fields, or names
- wrong constant, boundary, range, order, or iteration direction
- incorrect return / raise / break / continue
- callable replaced by a value or value used as a callable
- a whole function body that contradicts its callers or responsibility

For a small function, check each relevant statement once.

If the whole body is inconsistent, reconstruct only the smallest behavior supported by its callers, helpers, siblings, tests, and the reported contract.

### 4. PATCH
Once the defect and a minimal repair are concrete, patch immediately.

Do not keep investigating an already-supported repair.

Prefer a small production edit that restores existing behavior.
Do not refactor or redesign unrelated code.

### 5. VERIFY
After every patch:

1. run the smallest useful regression test or focused existing test;
2. rerun the issue reproduction;
3. check both affected and ordinary paths when relevant.

If the latest patch causes a regression or contradicts the contract, revert that patch only.

Keep earlier verified repairs.

### 6. LOCAL SWEEP
After the first verified repair, inspect the repaired function once for another concrete contradiction.

Then inspect nearby relevant code in the same file.

If the unresolved symptom or call path gives concrete evidence that another file in the same module participates, inspect that file too.

Some injected tasks contain multiple corruptions. Look for another supported defect, but do not perform broad repository-wide mutation hunting.

### 7. NEXT SYMPTOM
Return to the ledger.

For every unresolved explicit symptom, follow only the code needed to explain and repair it.

Do not stop merely because one symptom now passes.

### 8. STOP
When the reported symptoms are repaired or no further safe repair is supported:

- run the relevant tests;
- inspect the final diff;
- keep only justified production-source changes;
- stop.

## Boundaries

Use /testbed as the source of truth.

Modify production source only.

Do not modify tests, fixtures, snapshots, test data, configuration, packaging, grader/harness files, or import machinery.

Do not use network access, package installation, git history, alternate repository copies, site-packages copies, pristine copies, grader paths, or withheld material.

Use terminal, read_file, search_files, patch, and write_file directly when available.

Keep reads and searches bounded.
