**This round:** rank 3 · Δ vs baseline +0.111 on 6 paired instances · 1 verified.

## Round `r0001` — `5E4iMWRACSJrnbnCLNVfWXjHc5VRkgzRfaAzBiB1VXfkqPUg`

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
| `swe_fix` | 6 | 0.17 | — | — | unknown |

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
| `swe-fix-r0001-06` | 6 | `d2ee49024b904a84…` | tobymao__sqlglot.036601ba.func_pm_op_change__eh7z1d67 |
| `swe-fix-r0001-08` | 7 | `be3f359b973e88d5…` | python-openxml__python-docx.0cf6d71f.func_basic__4zrsk8co |
| `swe-fix-r0001-12` | 10 | `cd8a2d706be27656…` | tobymao__sqlglot.036601ba.func_pm_op_change_const__ikpi9udm |
| `swe-fix-r0001-16` | 3 | `b0558649c45a37af…` | scanny__python-pptx.278b47b1.func_basic__adjw18j5 |
| `swe-fix-r0001-17` | 1 | `41938baf15c23a6c…` | cantools__cantools.0c6a7871.func_basic__sldyccqp |
| `swe-fix-r0001-19` | 1 | `4f6db5c4633280b7…` | pygments__pygments.27649ebb.func_pm_class_rm_funcs__snpqqcj8 |

</details>