**This round:** rank 3 · Δ vs baseline +0.167 on 6 paired instances · 1 verified.

## Round `r0004` — `5E4iMWRACSJrnbnCLNVfWXjHc5VRkgzRfaAzBiB1VXfkqPUg`

**weight 0.1745** · score 0.1028

| | |
|---|---|
| episodes | 24 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1028 |
| standard error (incl. reference term) | 0.102778 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.1028 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 24 | 0.16 | — | — | frontier |

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
| `swe-fix-r0004-00` | 9 | `9733dc70b0ee1b74…` | cantools__cantools.0c6a7871.func_pm_remove_assign__y92u4hwd |
| `swe-fix-r0004-01` | 3 | `95385ae5d6b8ddfb…` | scanny__python-pptx.278b47b1.lm_rewrite__z0xlj083 |
| `swe-fix-r0004-03` | 3 | `037030b532d2a3c3…` | pygments__pygments.27649ebb.func_basic__4qr8ni7d |
| `swe-fix-r0004-04` | 1 | `81fa00652f050ea8…` | pylint-dev__astroid.b114f6b5.lm_rewrite__kxxx3vrz |
| `swe-fix-r0004-05` | 1 | `b65e93faf230e2ab…` | pylint-dev__astroid.b114f6b5.func_pm_ctrl_shuffle__yyc2h5n2 |
| `swe-fix-r0004-13` | 1 | `4339f044486911e9…` | oauthlib__oauthlib.1fd52536.func_basic__rxkupk6s |

</details>