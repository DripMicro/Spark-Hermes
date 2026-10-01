**This round:** rank 2 · Δ vs baseline +0.104 on 6 paired instances · 0 verified.

## Round `r0045` — `5DPhKi77DLciQzNDr6iCZ2cD41oHcV75vLdf82d3crVnERN6`

**weight 0.3179** · score 0.2438

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.2438 |
| standard error (incl. reference term) | 0.069025 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.1554 |
| score (mean d after the overfit and copy penalties) | +0.2438 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.11 | 0.21 | 0.0934 | frontier |

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
| `swe-fix-r0045-15` | 2 | `ec0c923bc53f2f48…` | pylint-dev__astroid.b114f6b5.func_basic__cpwpx163 |
| `swe-fix-r0045-16` | 4 | `c674f98d82c4c02a…` | tobymao__sqlglot.036601ba.func_pm_remove_cond__4k2hz7nk |
| `swe-fix-r0045-20` | 8 | `a5ce5a81014c4beb…` | tobymao__sqlglot.036601ba.combine_module__3uqs5jcs |
| `swe-fix-r0045-23` | 2 | `c8fc5c90ebd5d85c…` | tkrajina__gpxpy.09fc46b3.func_basic__lz7ase76 |
| `swe-fix-r0045-25` | 1 | `9b626d0fe5413bb0…` | python-openxml__python-docx.0cf6d71f.lm_rewrite__uskwg5dg |
| `swe-fix-r0045-27` | 2 | `4579fc45de074cff…` | tobymao__sqlglot.036601ba.func_pm_remove_cond__2nt6fq6w |

</details>