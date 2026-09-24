**This round:** rank 2 · Δ vs baseline +0.167 on 6 paired instances · 2 verified.

## Round `r0006` — `5DPhKi77DLciQzNDr6iCZ2cD41oHcV75vLdf82d3crVnERN6`

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
| `swe_fix` | 36 | 0.16 | — | — | frontier |

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
| `swe-fix-r0006-02` | 4 | `5d51b7c0b942af89…` | cantools__cantools.0c6a7871.combine_module__pjvgsc7d |
| `swe-fix-r0006-03` | 3 | `37fa2e83fc975fb6…` | scanny__python-pptx.278b47b1.lm_rewrite__n2tneu4a |
| `swe-fix-r0006-06` | 6 | `b957b5625b6b4b75…` | tobymao__sqlglot.036601ba.combine_module__x3rzaudu |
| `swe-fix-r0006-08` | 1 | `505fb4accaaf3a42…` | python-openxml__python-docx.0cf6d71f.lm_rewrite__l6qhe7eh |
| `swe-fix-r0006-09` | 1 | `8ba81362132eb66c…` | cantools__cantools.0c6a7871.func_basic__exzb81a5 |
| `swe-fix-r0006-25` | 1 | `2bc4b89919e9932e…` | cantools__cantools.0c6a7871.func_basic__mi6y0029 |

</details>