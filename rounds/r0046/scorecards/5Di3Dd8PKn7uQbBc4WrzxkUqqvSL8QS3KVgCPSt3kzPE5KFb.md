**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 0 verified.

## Round `r0046` — `5Di3Dd8PKn7uQbBc4WrzxkUqqvSL8QS3KVgCPSt3kzPE5KFb`

**weight 0.1427** · score 0.0968

| | |
|---|---|
| episodes | 47 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0968 |
| standard error (incl. reference term) | 0.058408 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0220 |
| score (mean d after the overfit and copy penalties) | +0.0968 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.12 | 0.21 | 0.0899 | frontier |

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
| `swe-fix-r0046-06` | 9 | `3b6021747c51d9e8…` | oauthlib__oauthlib.1fd52536.func_pm_remove_cond__s259zj7t |
| `swe-fix-r0046-07` | 2 | `da13c21c86fe5f6f…` | oauthlib__oauthlib.1fd52536.func_pm_remove_cond__fwwsp7kg |
| `swe-fix-r0046-10` | 4 | `91edbe7b8df09691…` | cantools__cantools.0c6a7871.func_basic__db2t1sw3 |
| `swe-fix-r0046-11` | 1 | `72e9d95a567671c1…` | tkrajina__gpxpy.09fc46b3.func_basic__3owy2590 |
| `swe-fix-r0046-12` | 1 | `1b9cd66c3c516ff9…` | pylint-dev__astroid.b114f6b5.pr_2380 |
| `swe-fix-r0046-13` | 4 | `506736eb095dd880…` | cantools__cantools.0c6a7871.lm_rewrite__4gi073yf |

</details>