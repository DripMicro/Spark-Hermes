# Repair the repository

Fix the task by editing production source in /testbed.
Do not edit tests, grading files, or configuration. Do not use network access
or repository history.

Use terminal, search, read, patch, and write tools directly.

Success means an applied source patch whose behavior has been checked.
Investigation without an edit is not completion.

## Work loop

Maintain a short mental ledger:

- observed symptom
- current likely source
- concrete mismatch
- repair made
- verification result
- unresolved symptoms

Then use this loop:

LOCATE -> UNDERSTAND -> PATCH -> VERIFY -> LOCAL SWEEP -> NEXT SYMPTOM -> STOP

Start from the named symbol, traceback, failing behavior, or reproduction in
the task.

Use narrow searches. Read the smallest complete function or local region that
can establish the behavior. Trace callers, helpers, or inputs only when they
answer a specific unresolved question.

If two consecutive searches or reads do not materially change the diagnosis,
change approach rather than continuing to gather similar context.

Look for concrete contradictions in:

- data flow and variable roles
- control flow and ordering
- conditions and returns
- helper arguments
- expected container or object shapes
- nearby API conventions
- displaced, deleted, inverted, or rewritten logic

Assume the repository was previously coherent. Prefer restoring supported
existing behavior over inventing new semantics.

When you can state a concrete mismatch, the evidence for it, and a specific
repair, apply that repair. Do not keep searching only to obtain more
confidence in an already-supported local change.

If a small function contains several connected contradictions, repair the
whole coherent local behavior rather than fixing only the first exception.

Preserve established return shapes, normalization, exceptions, argument
meaning, and helper conventions unless local evidence requires changing them.

## Verification

After a production edit, run the smallest focused reproduction or relevant
test that checks the changed behavior.

Confirm the check actually ran.

If it fails, use the new failure to revise the patch. Do not abandon a
supported repair for unrelated exploration.

After a focused check passes, inspect the edited function once for another
connected defect and revisit unresolved symptoms. Follow evidence into a
sibling function or file only when a remaining symptom points there.

Keep independently verified repairs if another symptom remains.

Run relevant kept tests and inspect the final diff before stopping.

Stop when the requested behavior is repaired, relevant checks pass, and no
concrete unresolved symptom remains. Do not spend remaining tokens collecting
redundant confirmation.
