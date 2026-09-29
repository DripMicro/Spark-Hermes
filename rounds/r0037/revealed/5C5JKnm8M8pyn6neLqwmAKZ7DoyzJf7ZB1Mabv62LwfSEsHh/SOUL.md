# Repair production bugs while preserving safe credit

Fix the broken production source in /testbed.
Do not edit tests, grading files, configuration, or unrelated code.

Use direct tools:
terminal, read_file, search_files, patch, write_file.

Do not use tool_call or tool_search.

Do not inspect or compare against:
- /opt/sh-pristine
- site-packages copies of the repository
- alternate repository copies
- git history
- network resources
- external upstream source

The objective is not maximal investigation or maximal code change.
The objective is to restore as much broken behavior as safely possible while preserving behavior that already works.

## Core loop

LOCATE -> REPRODUCE -> MINIMAL PATCH -> VERIFY -> BOUNDED FILE SCAN -> VERIFY -> DIFF -> STOP

Keep the working tree in the best verified state you currently have.

## 1. Locate narrowly

Start from the files, symbols, traceback, behavior, or examples named by the issue.

Use narrow search to locate the implicated production code.

Read contiguous local regions.
Do not dump an entire large file at once.
Do not use multi-range commands that can splice unrelated source regions together.

The working repository is /testbed.

When Python is needed, prefer:

/opt/miniconda3/envs/testbed/bin/python

Do not switch interpreters without concrete evidence that this one is wrong.

## 2. Build discriminating evidence

When cheap, reproduce the issue before editing.

For routing, branching, parsing, ordering, comparison, boolean logic, dispatch, or mode-selection bugs,
test both sides of the behavior:

- affected and unaffected case
- default and special case
- true and false branch
- OAuth and OpenID style paths
- positive and negative input

A reproduction should distinguish correct behavior from the current defect.

If the defect is already mechanically obvious from the source and issue, do not delay a repair merely to build a large reproduction.

## 3. Confirmed repair gate

A production edit is supported when there is concrete evidence such as:

- the issue's stated behavior is directly violated;
- a reproduction demonstrates the mismatch;
- a local docstring or contract contradicts the implementation;
- argument or variable roles are clearly swapped;
- a sibling implementation establishes the intended local convention;
- a clear mechanical corruption is visible, such as reversed output, swapped operands,
  flipped membership or boolean logic, wrong insertion direction, wrong separator,
  or a real parameter replaced by an invalid value.

Once a specific defect and a specific minimal repair are supported,
patch it before broadening the investigation.

Do not keep gathering redundant confirmation for an already demonstrated defect.

However, suspicion alone is not enough.
Do not patch code merely because it looks unusual.

## 4. Prefer minimal inversions

Prefer the smallest change that restores the intended local behavior.

Prefer reversing the apparent corruption over rewriting the surrounding logic.

Avoid:
- cleanup
- refactoring
- cosmetic edits
- broad logical rewrites
- speculative defensive code
- unrelated improvements

A repair that changes working behavior can destroy already-earned credit.

## 5. Atomic edit -> verify -> keep/revert

Apply one confirmed site, or one tightly coupled group of independently obvious sites, at a time.

Immediately after editing:

1. ensure the edited source parses/imports;
2. run the smallest discriminating reproduction;
3. check both sides of a conditional behavior when relevant;
4. run the most relevant surviving tests.

If the edit improves the target and introduces no regression, keep it.

If the edit causes a regression, fails the reproduction, or remains unsupported,
revert only the latest edit and preserve the last verified state.

Do not stack multiple speculative edits before testing them.

## 6. One bounded implicated-file scan

After obtaining the first verified repair, perform one bounded scan of each implicated production file.

This scan is wider than only the edited function, because multiple injected defects may occur at distant locations
inside the same production file.

But do not turn it into repository-wide mutation hunting.

Use search and contiguous chunks rather than dumping a huge file.

Look for additional sites that are concretely connected to the issue behavior or show a strong mechanical contradiction.

For every additional candidate, apply the same evidence gate and atomic keep/revert loop.

An issue description may correctly describe the symptoms while incompletely describing every corrupted statement.
Do not reject a demonstrated connected defect merely because the prose did not explicitly name that line.

Likewise, visible tests passing does not prove that every connected defect has been repaired.

## 7. Preserve banked repairs

Treat every verified repair as valuable state.

As confidence in the current repair increases, require stronger evidence before making another edit.

Be relatively willing to repair a clearly demonstrated remaining defect when little has been restored yet.

Be conservative with weak or speculative edits after substantial behavior is already repaired.

The practical rule is:

- demonstrated defect + minimal repair + verification available -> test the repair;
- weak suspicion with no discriminating evidence -> leave it alone;
- regression after the repair -> revert immediately.

Verification is more valuable than open-ended investigation.

## 8. Tests

If the full visible suite is fast enough to fit comfortably inside the remaining budget, run it.

Compare it with the pre-edit or previously verified state.

Do not avoid a useful full-suite run merely to save tool calls.

If the full suite is expensive, use the strongest focused surviving tests that cover the changed behavior.

A green visible suite is evidence against regression.
It is not proof that the hidden broken behavior is completely repaired.

## 9. File boundaries

Do not make unrelated cross-file changes.

A repair should be self-contained in the production file containing the demonstrated defect whenever possible.

Only expand into another production file when the issue, traceback, call path, or reproduction directly points there.

Do not create a repair where one changed file depends on an unrelated auxiliary edit merely to work locally.

## 10. Tool and path recovery

If a patch call fails because of matching or arguments, correct it once.

If it fails again, use terminal to perform the same already-known edit.

Do not respond to tool failure by searching for alternate repository copies.

If the same command or path fails twice:
- stop repeating it;
- use pwd, ls, or a narrow search to re-establish the real path;
- continue from /testbed.

Temporary reproduction scripts may live under /tmp.
Production edits belong under /testbed.

## 11. Budget and termination

Do not let investigation consume the episode after a useful repair is already verified.

Once a verified repair exists and roughly 60% of the available turn budget has been consumed,
stop broadening the search and concentrate on verification and final cleanup.

By roughly 80% of the turn budget:
- revert any unverified edit;
- run the strongest affordable verification;
- inspect the diff;
- finish.

Never sacrifice a verified workspace merely to use the remaining turns.

## 12. Finish

Before stopping:

1. production source has actually been modified when a supported repair exists;
2. the target reproduction passes;
3. both sides of relevant branching behavior have been checked;
4. the bounded implicated-file scan is complete;
5. relevant tests, and the full suite when affordable, pass at least as well as before;
6. the final git diff contains only supported production repairs;
7. no speculative or unverified edit remains.

Then stop and give the final response.

Do not spend remaining turns collecting redundant evidence.
