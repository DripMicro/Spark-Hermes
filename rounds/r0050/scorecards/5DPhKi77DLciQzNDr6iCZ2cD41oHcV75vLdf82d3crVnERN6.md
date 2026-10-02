**This round:** rank 5 · Δ vs baseline +0.067 on 6 paired instances · 1 verified.

## Round `r0050` — `5DPhKi77DLciQzNDr6iCZ2cD41oHcV75vLdf82d3crVnERN6`

**weight 0.2338** · score 0.1116

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1116 |
| standard error (incl. reference term) | 0.05244 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0445 |
| score (mean d after the overfit and copy penalties) | +0.1116 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.17 | 0.11 | -0.0611 | frontier |

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
| `swe-fix-r0050-04` | 6 | `f19dd0e043f61b1f…` | cantools__cantools.0c6a7871.func_basic__osfq8k96 |
| `swe-fix-r0050-07` | 3 | `2d5610349947de09…` | tobymao__sqlglot.036601ba.lm_rewrite__mxqbqknc |
| `swe-fix-r0050-08` | 2 | `af8c1ba118eeee7a…` | cantools__cantools.0c6a7871.func_pm_remove_cond__gqe3rcru |
| `swe-fix-r0050-09` | 5 | `30e866cdf5d64f18…` | oauthlib__oauthlib.1fd52536.lm_rewrite__4st59pwm |
| `swe-fix-r0050-10` | 5 | `029b45dd69c4f436…` | pylint-dev__astroid.b114f6b5.func_basic__zlo0vtm0 |
| `swe-fix-r0050-13` | 8 | `6626273c0dc86ab0…` | tkrajina__gpxpy.09fc46b3.func_basic__t25i8zki |

</details>