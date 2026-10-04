**This round:** rank 5 · Δ vs baseline +0.339 on 6 paired instances · 2 verified.

## Round `r0055` — `5Dh9YpJeTYKmgh9weSH9j24AtgEwVWoW37xsXakYGcpqVbKJ`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 6 |
| mean d (your share of checks passed − the baseline's, same instances) | — |
| standard error (incl. reference term) | — |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0000 |
| correctness gate | not passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** 6 window episodes < 8

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.43 | 0.11 | -0.3188 | frontier |

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
| `swe-fix-r0055-00` | 6 | `c48aa80e06a32b69…` | python-openxml__python-docx.0cf6d71f.combine_file__8uptj8pf |
| `swe-fix-r0055-05` | 5 | `6e97f85c9cca9880…` | tobymao__sqlglot.036601ba.combine_module__7x2zxhx8 |
| `swe-fix-r0055-07` | 10 | `650ed050eb296c56…` | python-openxml__python-docx.0cf6d71f.combine_file__ye8h6hmz |
| `swe-fix-r0055-15` | 4 | `835fed5f4b369994…` | pylint-dev__astroid.b114f6b5.pr_2599 |
| `swe-fix-r0055-17` | 7 | `a93db4f40ef93749…` | cantools__cantools.0c6a7871.combine_file__tbbk9e0p |
| `swe-fix-r0055-20` | 3 | `0b2e646a64f7265b…` | tkrajina__gpxpy.09fc46b3.func_pm_remove_cond__fhfj5atr |

</details>