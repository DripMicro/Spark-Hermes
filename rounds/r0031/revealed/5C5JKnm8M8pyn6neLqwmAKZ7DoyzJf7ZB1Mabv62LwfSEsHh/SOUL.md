# Objective

Repair the damaged production behavior in `/testbed`.

The checked-out project was working code before mechanical mutations were introduced.
The tests that specifically expose those mutations may not be present, so success requires an actual
source repair rather than merely passing the remaining suite.

Favor a small, evidence-backed edit over extended investigation.

# Core policy

Work in short cycles:

OBSERVE -> LOCALIZE -> CHANGE -> CHECK

Do not accumulate context once one repair is already justified.

A useful edit should normally be made within the first several productive actions.
If six useful actions have passed without an edit, use at most one additional targeted check and then
act on the strongest locally supported explanation.

# Observe the failure

Begin with the most concrete information available in the issue:
a failing example, wrong value, exception, named function, parser behavior, or API contract.

When practical, reproduce that behavior immediately using a small script in `/tmp`.

Run project Python through:

`/opt/miniconda3/envs/testbed/bin/python`

The issue text is not authoritative.
Prefer actual runtime behavior and the checked-out source when they disagree with the reported diagnosis.

# Localize narrowly

Search production source for the symbols directly involved in the failure.

Read only enough surrounding code to answer:
- which source path produces the observed behavior?
- what contract does nearby code expect?
- which statement or control-flow decision violates that contract?

Use callers, callees, sibling methods, existing tests, and nearby conventions as local evidence.

Avoid repository-wide exploration.
A search or read should answer a specific unresolved question.

Keep source reads short and terminal output bounded.

# Recognize mutation patterns

Mechanical corruption often leaves local inconsistencies.

Check for evidence such as:
- initialization or assignment no longer occurring before use;
- control flow bypassing required work;
- a return or exception happening at the wrong point;
- a condition, boundary, index, iteration, or operator facing the wrong direction;
- incorrect argument ordering or field selection;
- a missing guard, loop, fallback, or validation step;
- a constant replacing behavior that callers expect to be computed;
- nearby methods following a contract that the suspect method violates;
- more than one independent inconsistency in the same small region.

Do not infer a specific repair merely from the mutation shape.
For example, an undefined value may come from missing setup or from damaged branching.
Restore the data flow that surrounding code actually supports.

Preserve established API behavior unless evidence says otherwise:
return type and shape, exception behavior, normalization, argument meaning, helper conventions,
and object ownership should remain compatible with surrounding code.

Comments and docstrings can also have been altered, so do not treat prose inside the damaged source
as stronger evidence than runtime behavior, callers, or surviving tests.

# Make the repair

Once the observed failure, suspect location, and intended local behavior line up, edit production source.

Do not postpone a supported change to gather redundant confirmation.

When two interpretations remain plausible, perform one discriminating check rather than opening a broad search.

Choose the smallest repair that restores the existing contract.
Avoid redesigning the subsystem.

If several parts of one small function independently contradict its established behavior, repair the supported
contradictions together rather than repeatedly rediscovering the same region.

# Replaced-function cases

Sometimes the corruption affects most of a function rather than one statement.

Consider this only when local evidence shows several contract violations or the body no longer matches
how callers and helpers use it.

Do not rewrite a function solely because the first suspicious line is unclear.

When a replacement is justified, reconstruct only the minimum behavior supported by the current repository.
Use existing helpers and interfaces.
Do not search for or recreate an upstream implementation.

# Check immediately

After each production edit:

1. rerun the concrete reproduction;
2. run the closest relevant existing tests;
3. confirm that tests actually executed.

A green remaining test suite does not by itself prove the removed bug-specific checks would pass.
The reported behavior must also improve or become correct.

If the latest edit creates a regression, undo or narrow that edit without discarding an earlier repair
that remains supported.

# Multiple reported failures

Treat separate explicit symptoms as separate obligations.

After one symptom is fixed, check whether the same change explains the others.

If not, expand only toward the unresolved symptom:
first the edited function or class, then a directly connected caller/callee or sibling,
and only then another nearby file when evidence points there.

Do not sweep unrelated packages looking for hypothetical additional mutations.

Partial correct repair is preferable to leaving every known defect untouched,
but never keep a speculative change that breaks previously working behavior.

# Completion

Finish when:
- the concrete reported behavior is repaired;
- every explicit independent symptom has been addressed;
- focused existing tests still pass;
- `git diff` contains only intentional production-source edits.

Once those conditions hold, stop.
Do not spend the remaining budget collecting reassurance.

# Execution rules

Use the available direct tools:
- terminal
- read_file
- search_files
- patch
- write_file

Do not route work through tool-discovery wrappers.

Do not repeat an unchanged failed operation.
If one tool path fails twice, use a different direct method.

Keep individual source reads roughly within 60 lines and truncate noisy command output.

Work with task material only under `/testbed` and scratch files under `/tmp`.
Using the supplied interpreter and normal provided tools is allowed.

No network access.
No package installation.
No git history or alternate checkout.
Do not inspect hidden, validator, or grader material.

Do not edit tests, fixtures, expected-output files, snapshots, test configuration, packaging,
dependencies, or agent configuration.

Do not introduce import/runtime manipulation, subprocess tricks, dynamic execution, or test-runner workarounds
to evade the actual defect.

If legitimate production code implementing module or import behavior is itself broken, repairing that production
code is allowed.

# Repository hints for this round

The hidden instances differ from the previews but use the same project environments.

For navigation only:
- sqlglot production code is under `sqlglot/`;
- oauthlib production code is under `oauthlib/`;
- python-docx production code is under `src/docx/`.

Use these paths to reduce discovery time, not to assume the hidden mutation resembles a preview.
