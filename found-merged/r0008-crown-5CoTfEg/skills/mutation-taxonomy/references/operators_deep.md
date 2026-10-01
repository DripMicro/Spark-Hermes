# Operator playbook — every mutation family, its signature, search, and fix

These bugs are injected by a tool whose operators each leave a distinct fingerprint. Identify the
operator from the symptom (table below), then apply that operator's search and fix. Two or more
symptoms at once → a combine bug (see §10–11). When in doubt, run §1's recipe — it fits most.

| Symptom | Likely operator |
|---|---|
| `UnboundLocalError`/`NameError`; result object missing fields | §7 remove_assign |
| `AttributeError`: method or property missing | §9 class_rm_funcs |
| `AttributeError` on an attribute that should exist | §12 lm_rewrite (nonexistent attr) |
| Works but silently wrong values/units/ranges | §2 op_change, §3 op_change_const, §4 op_swap |
| Wrong branch, feature skipped/inverted | §5 ctrl_invert_if, §1 func_basic (and/or) |
| Wrong order in output; `__doc__` lost; behavior subtly off after "cleanup" | §6 ctrl_shuffle |
| Fluent-looking rewrite, verbose fresh docstring, edge cases broken | §12 lm_rewrite |
| Several unrelated wrongs in one file | §10 combine_file |
| Several wrongs across files of one package | §11 combine_module |

## §1 func_basic — a few lines twisted

Single or few-line edits. Sub-shapes seen: swapped function arguments (`MasterPlaceholder(parent,
shape_elm)` for `(shape_elm, parent)`); `and`↔`or` in a compound condition; inverted `not`;
default-value flip (`get_bool_opt(options, 'delphi', True→False)`); string assembly reordered
(`'/ns:'.join(x) + '/ns:'` for `'./ns:' + '/ns:'.join(x)`); a validation defused
(`_validate_margin_value(None)`); a **fake stub replacing a real method body** (a hardcoded dict
standing in for a real store, returning the wrong booleans); paired-name swap (open/close,
start/end); keyword-set names swapped (`PORTUGOL_KEYWORDS` ↔ `PORTUGOL_BUILTIN_TYPES`).
**Search:** read the named function fully; check every call's argument order against its
signature, every boolean's polarity, every default against callers, every `_validate_*` argument
against what it protects. **Fix:** restore each line to what its docstring/siblings/tests demand.

## §2 func_pm_op_change — an operator changed

Arithmetic/logic operator swapped: `first(largs - columns)` → `largs + columns`; `distance /
seconds` → `distance % seconds`; `/ 60 ** 2` → `// 60 ** 2`. Symptoms: wrong magnitudes, wrong
units, empty-vs-overlapping sets, divisions that explode or truncate.
**Search:** `search_files` the issue's quantities (speed, size, count, distance) and read every
arithmetic expression touching them; unit conversions and divisions are favorite targets; compare
each operator with the twin computation elsewhere (the same math in another class is the template).
**Fix:** restore the operator that makes the twin/units/dimension analysis correct.

## §3 func_pm_op_change_const — a constant or index changed

`self._tokens[self._index - 2]` → `- 3`; `value + 1`; `ext.cy = -value`. Off-by-one in indices,
shifted offsets, ±1 on dimensions.
**Search:** every numeric literal and index expression in the suspect function; check each against
what it indexes (`_index - N` counts tokens back — does N match the grammar?) and against sibling
functions using the same constant.
**Fix:** restore the constant the surrounding logic implies (loop bounds, grammar offsets,
sibling use).

## §4 func_pm_op_swap — operands swapped

`FORMAT_MAPPING or TIME_MAPPING` → reversed; `find(opening_chars…)` ↔ `find(closing_chars…)`;
`next_open_pos` ↔ `next_close_pos`. Reads naturally; comments survive.
**Search:** for every two-operand expression near the suspect code, ask which operand's value the
consumer expects first; for paired names (open/close, start/end, min/max, src/dst), verify each
use pairs the right two.
**Fix:** swap back the pair; then re-check the WHOLE block — swaps often come in sets.

## §5 func_pm_ctrl_invert_if — inverted control flow

The condition flips, or the two branch BODIES swap while the condition text stays valid.
**Search:** for each `if/else` in the function, ask: does this body accomplish what this condition
promises? Compare with the sibling implementation's branch order.
**Fix:** restore body↔condition pairing.

## §6 func_pm_ctrl_shuffle — statements reordered

A `return` moved **above the docstring** (→ `__doc__` becomes dead code); print/log lines
reordered (output order changes); a construction moved after its use; a guard moved out of its
branch. Symptoms: wrong output order, or "works" but tooling/docs/tests that read `__doc__` or
formatting fail.
**Search:** read the function top-to-bottom once asking "is every statement in causal order?"
(docs first, guards before use, build before return).
**Fix:** restore causal order; do not "fix" the docstring by moving it back until the return is
back in place.

## §7 func_pm_remove_assign — assignments deleted, replaced with `pass`

Up to **six-plus assignments deleted in one function**, including **whole constructor blocks**
(an object built with 5+ keyword arguments vanishing) and their comments. Symptoms:
`UnboundLocalError`/`NameError` on the deleted names, or — worse — a result object that is
**silently missing fields** (the deleted assignments fed it).
**Search:** `search_files` with `pattern: "pass$"`, `file_glob: *.py` over the suspect module —
a `pass` where an assignment should be is the literal fingerprint. Also `search_files` each field
the issue says is missing: if nothing assigns it anymore, you found the gutted constructor.
**Fix:** rebuild each deleted assignment from its name and its consumers (what type must `x` have
for the later `x.foo` to work?), from the sibling path, and from the constructor's keyword names.
Run the issue snippet between restorations.

## §7b func_pm_remove_loop / func_pm_remove_wrapper — deleted validation loops and error-handling wrappers

- **remove_loop:** the FOR-LOOP that validated function arguments is deleted (the block
  raising a sentinel exception per unsupported argument). The function then processes
  UNVALIDATED input. **Search:** in the suspect function, look for missing iteration over
  its own parameters — a contract that says it validates/normalizes each X but a body that
  never loops. The sibling function still has its validation loop; the mutated one does not.
  **Fix:** restore the loop: validate each argument, raise/return the documented fallback.
- **remove_wrapper:** the TRY/EXCEPT wrappers around unsafe operations are removed. Code
  that caught TypeError/KeyError and yielded a graceful fallback now lets the raw exception
  propagate. **Symptom:** a raw crash exactly where the old behavior was a soft fallback.
  **Search:** find where the crash surfaces and walk down the call chain — a deleted
  try/except with its handler body. The fallback value is recoverable from tests and callers.
  **Fix:** restore the try/except with the exact fallback behavior.

## §8 func_pm_remove_cond — a guard removed

A condition block deleted: a `continue` filter gone, an early `return` gone, an `if x:` wrapper
removed so code runs unconditionally (or never). Symptoms: items processed that should be
excluded; a crash on the edge case the guard protected.
**Search:** for every loop/branch in the suspect function, ask what input the issue says breaks —
then check whether the filter that excludes that input still exists. Complementary filter pairs
(`exclude_extended` / `exclude_normal`) are a favorite: one of the pair gets deleted.
**Fix:** restore the guard from the complementary filter and the callers' flags.

## §9 func_pm_class_rm_funcs — whole methods removed from a class

A `@property`/`@lazyproperty`/method deleted from a class (an APP1-marker property, a font
lazyproperty, a `get_tokens_unprocessed` override). Symptoms: `AttributeError` on the method, or
the behavior hook silently gone.
**Search:** `search_files` the method name in the package — absent definition + present callers =
removed method. The callers and the class's siblings tell you the contract.
**Fix:** restore the method: signature from the callers, body from the docstring (usually removed
with it — the pattern is recoverable from what the callers expect it to return) and from sibling
methods doing analogous work. Mind decorators (`@property`, `@lazyproperty`).

## §9b func_pm_class_rm_base — a base class removed

A class's parent deleted from its definition (`class X(Y)` → `class X`) or the `import` feeding
it removed. Symptoms: `TypeError: object.__new__() takes no parameters`, methods that "should"
exist via inheritance missing, `super()` breaking, MRO errors.
**Search:** for the suspect class, read its `class X(...)` line and check every base still
resolves (is the defining import present? does the base itself exist?). Compare with a sibling
type of the same family (other markers, other loaders) — they share base patterns.
**Fix:** restore the base reference and, if the import was removed, that too. Verify with the
file's test module.

## §10 combine_file — several micro-mutations in ONE file

2–6 sites in the same file, each a §1–§8 shape: attribute swap (`anchor`↔`address`), dimension
swap (`cx`↔`cy`) plus `+1`/`-value` twists, `%d`→`%s`, an altered URI string, `return inline` →
`return None`, `True`↔`False`, reversed string assembly, an extra call parenthesized. Comments are
sometimes EDITED to match the mutation — do not trust a comment that justifies the wrong line.
**Search:** after fixing the first site, `search_files` the file for every sibling shape: other
assignments touching the same attributes, other format strings, other booleans, other returns.
**Fix:** fix all sites, then run the file's test module — one missed site keeps the tests red.

## §11 combine_module — the same across MULTIPLE files of one package

Like §10 but spread over 2–3 files of the same package (e.g. `oxml/shape.py` + `oxml/styles.py`).
**Search:** after the first file is fixed and tests still fail, `search_files` the failing
symbols across the package; check every file the issue's traceback touched plus one neighbor.
**Fix:** per §10, per file.

## §12 lm_rewrite — a language model rewrote the whole function

The fingerprint: the function now carries a **fresh verbose docstring** (an "Args:/Returns:"
block on an old function that never had one), the body restructured with renamed locals, merged
or split branches, and — critically — **special cases dropped and nonexistent attributes
referenced**. Real examples: a proxy `__getattr__` that lost its `_proxied`/`__dict__` guards and
now raises `AttributeError` on the proxy's own machinery; a rewrite calling `dLbl.has_tx_rich`
where no such property exists; a loop rewritten so the timeout logic no longer tracks the
deadline.
**Search:** (1) read the fresh docstring as the SPEC — it describes the original behavior the
rewrite was supposed to keep; (2) list every branch/special case the callers and tests imply
(private/dunder names, `is None`, empty inputs, fallback paths) and check the body still handles
each; (3) `search_files` every attribute/method the rewritten body touches — each must exist;
(4) check every `return` path returns what the docstring promises.
**Fix:** rebuild the body from the docstring + callers + tests; keep nothing from the rewrite
that you cannot justify against that contract.
