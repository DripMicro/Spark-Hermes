# Fix the production bug in /testbed

Work on the smallest supported production repair. Do not turn the task into an investigation project.

1. Start from the issue, traceback, failing behavior, and named symbols. Locate the implicated production code and read the relevant function or block.

2. As soon as you can state a concrete defect and a minimal repair, edit the production source. Do not postpone an already-supported repair to gather redundant evidence.

3. Verify the edit immediately with the smallest useful reproduction or test. For routing, branching, or mode-selection logic, check both the affected path and the ordinary path. If the latest edit makes behavior worse, revert that edit.

4. After the first verified repair, do exactly one bounded completion pass. Re-read the repaired function and nearby relevant code in the same file for another concrete defect connected to the behavior. If the issue, call path, or reproduction gives concrete evidence that another file in the same module participates, inspect only that file too.

Some tasks contain multiple independent corruptions. One fixed symptom or a green focused test is therefore not always enough. Patch an additional site only when behavior, tests, or the local contract gives concrete evidence for it.

5. Run the relevant tests. Run the full visible suite when it is reasonably fast. Inspect the final diff, keep only supported production edits, and stop.

Use /testbed as the source of truth. Do not inspect alternate repository copies, site-packages copies, git history, upstream sources, or the network. Do not edit tests, grader/harness files, or unrelated code. Avoid broad mutation hunting, refactoring, cleanup, and speculative fixes.
