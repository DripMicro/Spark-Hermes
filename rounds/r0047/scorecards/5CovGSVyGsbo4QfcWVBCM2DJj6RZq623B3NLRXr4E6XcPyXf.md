**This round:** not ranked · Δ vs baseline -0.111 on 6 paired instances · 0 verified.

## Round `r0047` — `5CovGSVyGsbo4QfcWVBCM2DJj6RZq623B3NLRXr4E6XcPyXf`

**weight 0.1993** · score 0.1528

| | |
|---|---|
| episodes | 12 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1528 |
| standard error (incl. reference term) | 0.152778 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.1528 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.11 | 0.21 | 0.0951 | frontier |

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
| `swe-fix-r0047-03` | 1 | `e22ea348286f3079…` | cantools__cantools.0c6a7871.combine_file__50pf4pnz |
| `swe-fix-r0047-06` | 4 | `421732012cad029f…` | marshmallow-code__marshmallow.9716fc62.lm_rewrite__5ue0iqa9 |
| `swe-fix-r0047-07` | 1 | `503c1daf4b52497a…` | tkrajina__gpxpy.09fc46b3.lm_rewrite__rc6glspq |
| `swe-fix-r0047-08` | 9 | `38928a20603b6d96…` | cantools__cantools.0c6a7871.combine_file__0t45ljxl |
| `swe-fix-r0047-10` | 1 | `d346cd6a835fef12…` | python-openxml__python-docx.0cf6d71f.lm_rewrite__jv7un8hq |
| `swe-fix-r0047-11` | 2 | `32f6a0e527ce05a3…` | tobymao__sqlglot.036601ba.lm_rewrite__fdnja206 |

</details>