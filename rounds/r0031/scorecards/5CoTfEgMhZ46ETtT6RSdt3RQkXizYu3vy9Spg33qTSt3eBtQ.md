**This round:** rank 3 · Δ vs baseline +0.167 on 6 paired instances · 1 verified.

## Round `r0031` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.3000** · score 0.1730

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1730 |
| standard error (incl. reference term) | 0.07038 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0829 |
| score (mean d after the overfit and copy penalties) | +0.1730 |
| correctness gate | passed |
| Δe | api_calls -0.01 · tool_calls +0.02 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.16 | 0.00 | -0.1551 | frontier |

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
| `swe-fix-r0031-01` | 1 | `fd46e58243209a24…` | tobymao__sqlglot.036601ba.func_pm_ctrl_shuffle__17mtng5y |
| `swe-fix-r0031-02` | 1 | `0be9f9d5a21d33e4…` | tobymao__sqlglot.036601ba.lm_rewrite__qgqm56ph |
| `swe-fix-r0031-03` | 4 | `5d376c1a7d863177…` | python-openxml__python-docx.0cf6d71f.func_pm_ctrl_invert_if__8n2ui6bu |
| `swe-fix-r0031-05` | 4 | `f3d6e6d08c419cdc…` | oauthlib__oauthlib.1fd52536.lm_rewrite__1oh6objh |
| `swe-fix-r0031-06` | 1 | `54982e247a491369…` | tobymao__sqlglot.036601ba.lm_rewrite__5d9czzp5 |
| `swe-fix-r0031-07` | 8 | `d37893f260c64dd5…` | oauthlib__oauthlib.1fd52536.func_pm_remove_cond__u1l8l7is |

</details>