---
name: repo-traps
description: Compact project-specific hazards for known repositories. Open only when the repository is recognized.
---

# Repository traps

Use this only when the current repository matches one below. Do not browse these notes speculatively.

## python-docx / python-pptx

Public API methods commonly delegate to XML `CT_*` element classes. If the public method looks correct, inspect one level below before widening the search. Preserve exact XML behavior and do not touch fixture files.

## astroid

Inference code is generator-sensitive. `yield`, `return`, and the `Uninferable` sentinel are not interchangeable. Warnings may fail tests, and strict expected-failure tests can fail if an unrelated behavior is accidentally repaired. Change only the behavior named by the issue.

## pygments

Many checks compare exact or snapshot-like output. Never regenerate expected output. For delegating lexers, verify root/language lexer ordering against sibling implementations rather than inventing a new arrangement.

## cantools

CLI text is exact: whitespace and line breaks matter. Keep pytest quiet and never modify files under test-data directories merely to make output agree.

## oauthlib

Protocol strings are contracts: parameter names, headers, error slugs, and status values must be exact. Compare a suspect grant or endpoint with its sibling and shared base implementation.

## sqlglot

Dialect implementations are highly parallel. A sibling dialect is often the strongest reference for a mutated method. Leave fixtures and expected SQL files untouched.

## gpxpy

`None`, `0`, and empty values have distinct meanings. Compare the same method across point/route/track siblings. For speed or distance logic, guard invalid or zero time intervals rather than inventing a replacement formula.

## Anything else

Do not extrapolate these repository-specific rules. Return to the issue, surviving tests, docstrings, callers, and sibling code.
