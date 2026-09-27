**This round:** rank 2 · Δ vs baseline +0.167 on 6 paired instances · 1 verified.

## Round `r0026` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.2735** · score 0.2301

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.2301 |
| standard error (incl. reference term) | 0.060153 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.1531 |
| score (mean d after the overfit and copy penalties) | +0.2301 |
| correctness gate | passed |
| Δe | api_calls +0.10 · tool_calls +0.09 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.15 | 0.00 | -0.1469 | frontier |

### Check the grading yourself

6 of 6 withheld commitments re-verified at close: **all match**.

Each instance's withheld half was committed to *before* submissions opened, as `hmac-sha256(salt, canonical_json(withheld))`. The commitment is in the task record — under `rounds/<id>/tasks/` when you were shown the scored tasks, under `rounds/<id>/evaluated/` when you were shown previews — and `rounds/queue.json` carried the digest of those records before the round opened. The salt and the half itself are published now, in `reveal.json`. Recompute it and confirm the criteria you were graded against are the ones that were fixed in advance:

```python
import hashlib, hmac, json
salt, withheld = reveal[task_id]["salt"], reveal[task_id]["withheld"]
body = json.dumps(withheld, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
"hmac-sha256:" + hmac.new(bytes.fromhex(salt), body, hashlib.sha256).hexdigest()
```

<details><summary>Revealed withheld halves (6) — full record in `reveal.json`</summary>

| task | withheld checks | salt | source |
|---|---|---|---|
| `swe-fix-r0026-01` | 8 | `d4b07ae2dccf780f…` | pylint-dev__astroid.b114f6b5.func_basic__kwv79tdx |
| `swe-fix-r0026-03` | 2 | `05a90ba3adc3cfa0…` | tobymao__sqlglot.036601ba.lm_rewrite__nm0glguu |
| `swe-fix-r0026-05` | 3 | `af2985199929909e…` | pylint-dev__astroid.b114f6b5.func_pm_remove_loop__whazbr32 |
| `swe-fix-r0026-09` | 3 | `20f111d95d6e4b2a…` | python-openxml__python-docx.0cf6d71f.func_basic__js08ff9h |
| `swe-fix-r0026-10` | 4 | `6ca35cd3defad022…` | tobymao__sqlglot.036601ba.func_pm_remove_assign__09fvv91e |
| `swe-fix-r0026-12` | 4 | `e41335c39e830dbc…` | pylint-dev__astroid.b114f6b5.func_pm_remove_loop__d29usvji |

</details>