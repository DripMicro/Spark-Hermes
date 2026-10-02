**This round:** rank 5 · Δ vs baseline +0.167 on 6 paired instances · 1 verified.

## Round `r0048` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.1818** · score 0.1577

| | |
|---|---|
| episodes | 42 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1577 |
| standard error (incl. reference term) | 0.071163 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0666 |
| score (mean d after the overfit and copy penalties) | +0.1577 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 1 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.13 | 0.11 | -0.016 | frontier |

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
| `swe-fix-r0048-02` | 4 | `98aaf8044567f63a…` | tkrajina__gpxpy.09fc46b3.func_pm_op_break_chains__c7h9xxea |
| `swe-fix-r0048-03` | 6 | `754f7cf99162f3fd…` | oauthlib__oauthlib.1fd52536.combine_module__b4neuv4o |
| `swe-fix-r0048-04` | 1 | `4408cc10699c89db…` | tobymao__sqlglot.036601ba.lm_rewrite__j3y8z8f5 |
| `swe-fix-r0048-05` | 1 | `0c1cb908a76e5f44…` | cantools__cantools.0c6a7871.func_basic__e1wnk87z |
| `swe-fix-r0048-06` | 1 | `6d48ac684f73efd5…` | cantools__cantools.0c6a7871.lm_rewrite__3xf41h9c |
| `swe-fix-r0048-07` | 8 | `3416a45e70884506…` | pylint-dev__astroid.b114f6b5.func_basic__xeyrub1r |

</details>