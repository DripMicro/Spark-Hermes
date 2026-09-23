---
name: bug-shapes
description: The forms an injected edit takes and the search that finds each one. Open after the repro runs, before the first edit.
---

# The edit disagrees with what was not edited

These bugs are edits to working code. The docstring, the type hints, the next branch, the sibling function, the callers, and the surviving tests were not part of the edit. Where the code contradicts them, that is the line.

## How many sites

Decide this before you edit, because it decides when you stop.

One site: the issue describes one misbehaviour and names one function. Fix it, run the covering tests, sweep, stop. Still re-read the lines you changed against the signature they call. The odd line is often not the whole site.

Several sites: the issue is a list, it names several symbols, or it says the output is wrong in more than one way. A large set of broken tests points the same way. The edits are independent. Each one you fix is credit. Missing the last one does not take away the ones you fixed.

After the first fix, read the whole file, not only the function you changed, and check each function against the shapes below. Then read the other modules the issue names.

A whole function can be rewritten into something that reads cleanly and still does the wrong job. Compare it with its docstring and with what callers expect, not with its own internal consistency.

## Shapes, in the order to check

1. Inverted condition. The wrong branch runs, or a feature is skipped, and nothing crashes. Read every `if`, `elif`, and `while` in the suspect function. Check `not`, `==` against `!=`, `and` against `or`, `in` against `not in`, and `<` against `<=`.

2. Swapped or renamed names. `TypeError` on arguments, `UnboundLocalError`, `NameError`, or an attribute error on `None`. Match call arguments to the signature by name, not by position. Count where each local is assigned against where it is read. A name read on a path where it was never assigned is the unbound-local shape. Two arguments of the same type swapped in a superclass call is a common edit.

3. Off by one. `IndexError`, the first or last element wrong, an empty result. Check every slice, `range`, index, and `len`. Compare `i` with `i + 1`, `len(x)` with `len(x) - 1`, and a half-open end with a closed one.

4. Wrong literal or operator. The type is right and the value is wrong, or a test fails on an exact string. Collect the numbers, strings, format pieces, and operators in the block and compare each with the same thing elsewhere in the file. A default argument, `+` where `-` belongs, `/` where `//` belongs, dropped parentheses, a changed separator.

5. Something removed. Nothing on the screen looks odd. The clue is absence. An argument dropped from a call whose target still accepts it. A keyword that every sibling call passes and this one does not. A method present on sibling classes and missing here. A `return` or an assignment gone. Count the arguments against the signature. One edit can both reorder arguments and drop one, so fixing the order does not finish the site.

6. Dropped guard. A crash on empty input or `None`. For every attribute access and index, ask what happens when the value is empty or missing. A missing early return, a `try` that lost its handler, a loop that lost `break` or `continue`.

7. Changed return. The caller fails far from the bug, or the wrong type comes back. Check every `return`: the right name, the right tuple order, a branch that falls off the end and returns `None`.

8. Exception handling. The wrong class is raised, or an exception is swallowed. Check each `except`: the class, the re-raise, the cleanup.

## Symptom back to shape

- `UnboundLocalError` or `NameError`: shape 2.
- `TypeError` about arguments: shape 2.
- `IndexError`: shape 3.
- Attribute error on `None`: shape 5 or 6.
- Wrong value, right type: shape 4 or 1.
- Exact text mismatch: shape 4.
- `TypeError` on an arithmetic operator with `None`: shape 5, a field the parser stopped filling.
- Many unrelated tests failing: several sites, or one edit in a shared helper.

## Before the edit

Say one sentence: line L of function F in file P should do X and instead does Y. If you cannot, take the strongest candidate above and change that. Try one candidate at a time and re-check. Several speculative edits at once leave you unable to tell which one to keep.
