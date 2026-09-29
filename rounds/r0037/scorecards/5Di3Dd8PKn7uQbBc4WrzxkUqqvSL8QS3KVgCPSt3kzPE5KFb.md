**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 0 verified.

## Round `r0037` — `5Di3Dd8PKn7uQbBc4WrzxkUqqvSL8QS3KVgCPSt3kzPE5KFb`

**weight 0.2247** · score 0.1214

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1214 |
| standard error (incl. reference term) | 0.054548 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0516 |
| score (mean d after the overfit and copy penalties) | +0.1214 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.14 | 0.39 | 0.2515 | frontier |

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
| `swe-fix-r0037-00` | 1 | `f326082aba84a659…` | tobymao__sqlglot.036601ba.lm_rewrite__nruadebf |
| `swe-fix-r0037-01` | 5 | `699e1bad0d67e553…` | tobymao__sqlglot.036601ba.combine_module__yvb3ed9d |
| `swe-fix-r0037-03` | 4 | `efb2f290a795b971…` | oauthlib__oauthlib.1fd52536.combine_module__dzs71zi4 |
| `swe-fix-r0037-04` | 1 | `9d208b3fb77fae5b…` | tobymao__sqlglot.036601ba.lm_rewrite__sgfp4ebt |
| `swe-fix-r0037-06` | 1 | `0ae74adbbbdf3497…` | tobymao__sqlglot.036601ba.lm_rewrite__hdfmp46a |
| `swe-fix-r0037-07` | 2 | `8646d69a90ea0303…` | cantools__cantools.0c6a7871.func_basic__eil6eqdj |

</details>