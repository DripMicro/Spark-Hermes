---
name: mutation-taxonomy
description: Use symptom and code evidence to recognize mechanical source mutations, including multi-site edits and whole-function rewrites.
---

# Mutation triage

Use this skill only when the failure looks like a source mutation and the faulty
line is not yet clear. Read the matching section of references/operators.md only
if this page is insufficient. For an unfamiliar repository, use the matching
section of references/codebases.md. Read only the reference you need.

## Route from observed failure, then verify the route

- Undefined local or missing result field: deleted or displaced assignment.
- Missing method, property, or inherited behavior: removed class member or base.
- Wrong values or units: operator, constant, operand, default, or type conversion.
- Wrong branch or missing validation: inverted condition, swapped bodies, or lost guard.
- Wrong order, unreachable work, lost function documentation: statement shuffle.
- Plausible long replacement with broken edge behavior: whole-function rewrite.
- Several unrelated symptoms: independent sites in one function, one file, or
  adjacent package files. Do not stop when only the first symptom is fixed.

A symptom is a search hint, never proof. Look for contradiction with surviving
tests, caller contracts, sibling implementations, types, and data flow. Comments
and docstrings can themselves be changed by a rewrite.

## Search and edit

Read the suspect function in a bounded slice. For every line, ask what values it
accepts, changes, and returns. Match call arguments with the callee signature.
Check all branches and the missing-path cases: empty input, None, boundaries,
fallback, exception, and default. Check exact output and side effects.

Edit the first evidenced mismatch early. Verify it, then make a short symptom
ledger: each issue claim must map to a fixed site or an observed passing path.
Sweep neighboring tests before finishing. Do not copy a sibling blindly; preserve
the local API and branch differences.

## Deep playbook (optional)

`references/operators_deep.md` holds the long-form per-shape recipes with concrete
examples. Load it ONLY when the quick table above does not resolve the shape you are
facing — it is larger and rides along in every later step once opened.