# Fix the injected bug in /testbed

Working code in `/testbed` was mechanically edited to break it. Put it back. No one will answer questions.

## How this task overrides the runtime notes below

The runtime notes after this section talk about prerequisite checks, not guessing, and verifying before
you act. **For this task, the order is reversed: edit first, verify after.** You have about 25 tool calls
before the budget cuts you off. Runs that keep gathering context until they are sure score 0 — almost all
of them had already read the broken line in their first few calls and never changed it. An untouched tree
scores 0 and a wrong edit scores 0, so an informed guess applied as a patch is never worse and often wins.

**Three runtime rules end your run at 0 — never trigger them:**
- A reply with no tool call ends the run. Until you are finished, every reply contains a tool call. Never
  write a fix in a message: **the moment your reasoning contains a corrected line, your next call is
  `patch` with it.**
- A reply that thinks too long is cut off and ends the run. Think in a few short sentences, then act.
- Repeating the same call (same command or same read) about five times halts the run. Change something
  every call.

**Deadline: by your 6th tool call you have patched a `/testbed` file.**

## The loop

1. **Locate** (1–2 calls): `grep -rn "<name from the issue>" /testbed --include=*.py | grep -v /tests/ | head -20`.
2. **Reproduce** (1–2 calls): `write_file` the issue's snippet (or a minimal call of the named function)
   to `/tmp/r.py`, run `cd /testbed && /opt/miniconda3/envs/testbed/bin/python /tmp/r.py 2>&1 | tail -n 25`.
   The last `/testbed` frame, or the function returning the wrong value, is the suspect.
3. **Read the suspect function** once: `read_file` with `offset` and `limit` ≤ 60.
4. **Audit it, line by line, in your reasoning:** for each line, "matches" or "does not match" what its
   name, neighbours and callers imply (the docstring may have been edited too). Keep it to one short line
   per suspicious line, not an essay. Look hard for these fingerprints:
   - a lone `pass` where an assignment or `return` belongs; a variable used before any assignment — the
     assignment was deleted: write it back above its first use (`x = obj.x` style);
   - a case nothing handles any more: a deleted `if` guard (a filter or `raise` that rejected bad input,
     a `None`/empty check), a deleted loop (one item handled where all should be), a deleted
     `try`/`except` fallback — add the missing statement back, modelled on the surrounding code;
   - a `return`/`raise` placed too early with code after it; a docstring that is not the first statement;
   - a flipped operator or comparison, `not` added or dropped, an off-by-one constant, swapped arguments
     or swapped variables;
   - a method callers use that no longer exists — write it back, modelled on its siblings;
   - a body that returns something else than its callers expect, or simulates logic ("simulate", fake
     lookups, a stub that should `raise NotImplementedError` but returns a value).
5. **Patch the first "does not match" line in your very next call.** Then rerun `/tmp/r.py`.
   **No line stands out?** Then the whole body was rewritten: it reads plausibly but no longer does what its
   name, callers and the issue say. Do not keep reading — rewrite the body minimally so it does exactly
   that (reuse the helpers its siblings use), patch it now, and let `/tmp/r.py` judge.
6. **Finish the audit — edits come several at a time.** Re-read the lines you patched once and fix every
   other mismatch there (literals, argument order, swapped names, a dropped branch). If `/tmp/r.py` still
   prints anything the issue says is wrong, check sibling functions, then **sibling files of the same
   package directory** (e.g. `diagnostics/database.py` and `diagnostics/did.py`, or two dialect modules):
   `grep -rn "<name>" <that directory> | head -20`, audit the hit and patch it.
7. **Check**: `cd /testbed && /opt/miniconda3/envs/testbed/bin/python -m pytest <test file for that module> -q -x -p no:cacheprovider 2>&1 | tail -n 8`
   (gpxpy: `test.py` at the root). A failure you caused: narrow or revert that edit. Green local tests do
   **not** prove you are done — the graded tests are hidden; `/tmp/r.py` matching the issue is the check.
   Then stop with one line.

## Limits

- **Never list, read or run anything under `/ep`, `/runner` or elsewhere outside `/testbed` and `/tmp`**
  — not even `ls`. Touching the grader's paths disqualifies the run.
- Only the file(s) holding the bug are graded; fix it there. If any test that passed before now fails,
  the score is 0 — keep edits minimal.
- Call these tools directly: `terminal`, `read_file`, `write_file`, `patch`, `search_files`. Never
  `tool_call`, `tool_search` or `tool_describe`; there is no `bash`, `Read`, `Grep` or `Edit`.
- **Do not hunt for the answer elsewhere.** No grepping `tests/` or fixtures to learn what the code should
  do, no `git` (one commit, no history), no `pip download`, no `find /`, no recalling "the upstream
  version". There is no other copy of the project (`/opt/sh-pristine` is the same broken code). The issue
  and the code in front of you are the spec.
- **Never let a tool print more than ~60 lines.** One whole-file read (30k+ characters) is what makes runs
  lose track of their tools and fail. Every `read_file` — also in a batch of parallel calls — gets a `limit`
  of at most 60, e.g. `read_file(path="/testbed/pkg/mod.py", offset=240, limit=60)`, with the offset found
  by `grep -n` first. Every `terminal` command ends in `| head -n 40` or `| tail -n 40`. Never `cat` a file.
- If a result says "is not a deferrable tool" or "Tool loop warning", your next call is plain `terminal`
  with the command you meant — nothing else.
- Never: network, `pip`; editing or adding tests or test config; writing outside `/testbed` and `/tmp`;
  `inspect`, `importlib`, `subprocess`, `pytest`, `exec`, `eval` in the fix.

## Remember

Patch by your 6th call. A corrected line in your head goes into `patch` at once. Every reply has a tool
call. Stay inside `/testbed` and `/tmp`, keep outputs under ~60 lines, and finish the audit before you stop.
