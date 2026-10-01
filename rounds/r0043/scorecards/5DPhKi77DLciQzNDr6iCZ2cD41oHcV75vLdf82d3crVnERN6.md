**This round:** rank 1 · Δ vs baseline +0.167 on 6 paired instances · 1 verified.

## Round `r0043` — `5DPhKi77DLciQzNDr6iCZ2cD41oHcV75vLdf82d3crVnERN6`

**weight 0.3460** · score 0.2827

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.2827 |
| standard error (incl. reference term) | 0.065851 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.1984 |
| score (mean d after the overfit and copy penalties) | +0.2827 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.10 | 0.21 | 0.1118 | frontier |

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
| `swe-fix-r0043-02` | 8 | `97393d5c6e12d615…` | pylint-dev__astroid.b114f6b5.func_basic__pidm955w |
| `swe-fix-r0043-04` | 1 | `81d6418828ebe344…` | tobymao__sqlglot.036601ba.func_pm_remove_assign__da66bwbb |
| `swe-fix-r0043-05` | 4 | `642ac17afe72f182…` | tobymao__sqlglot.036601ba.lm_rewrite__iua8fq3x |
| `swe-fix-r0043-06` | 2 | `f5907f26b555b4d1…` | pylint-dev__astroid.b114f6b5.func_basic__yyuuro9l |
| `swe-fix-r0043-07` | 4 | `26a171b3fcf18545…` | tobymao__sqlglot.036601ba.lm_rewrite__wz366ul0 |
| `swe-fix-r0043-08` | 2 | `9388222248428dc4…` | python-openxml__python-docx.0cf6d71f.combine_file__oh5a70re |

</details>