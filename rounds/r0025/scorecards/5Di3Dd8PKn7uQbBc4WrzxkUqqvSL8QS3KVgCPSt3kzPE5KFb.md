**This round:** rank 5 · Δ vs baseline +0.019 on 6 paired instances · 0 verified.

## Round `r0025` — `5Di3Dd8PKn7uQbBc4WrzxkUqqvSL8QS3KVgCPSt3kzPE5KFb`

**weight 0.1898** · score 0.1672

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1672 |
| standard error (incl. reference term) | 0.060751 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0894 |
| score (mean d after the overfit and copy penalties) | +0.1672 |
| correctness gate | passed |
| Δe | api_calls -0.25 · tool_calls -0.30 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.15 | 0.00 | -0.1469 | frontier |

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
| `swe-fix-r0025-00` | 9 | `ff71f2f0fc563b90…` | tobymao__sqlglot.036601ba.combine_file__dyfeesvf |
| `swe-fix-r0025-01` | 6 | `4fd4c1b2f164b63b…` | cantools__cantools.0c6a7871.lm_rewrite__155sxo9q |
| `swe-fix-r0025-05` | 6 | `9a9e122b273e0333…` | oauthlib__oauthlib.1fd52536.combine_file__oni9ccvi |
| `swe-fix-r0025-06` | 9 | `e1faf5a86b2ec494…` | cantools__cantools.0c6a7871.combine_file__h5p7hsu6 |
| `swe-fix-r0025-07` | 3 | `bd98220ad925e6f5…` | andialbrecht__sqlparse.e57923b3.combine_module__cwv6tm4l |
| `swe-fix-r0025-11` | 1 | `839d159aa0a23f04…` | pylint-dev__astroid.b114f6b5.func_basic__hqgj2c2c |

</details>