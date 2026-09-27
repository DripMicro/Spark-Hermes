**This round:** rank 3 · Δ vs baseline +0.139 on 6 paired instances · 3 verified.

## Round `r0022` — `5DPhKi77DLciQzNDr6iCZ2cD41oHcV75vLdf82d3crVnERN6`

**weight 0.2781** · score 0.1736

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1736 |
| standard error (incl. reference term) | 0.051561 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.1076 |
| score (mean d after the overfit and copy penalties) | +0.1736 |
| correctness gate | passed |
| Δe | api_calls +0.14 · tool_calls +0.06 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.14 | 0.00 | -0.1426 | frontier |

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
| `swe-fix-r0022-00` | 4 | `3e5066e6b89a74af…` | tobymao__sqlglot.036601ba.func_pm_remove_loop__ulwxz6si |
| `swe-fix-r0022-02` | 2 | `fd3ef7644aeb6f4b…` | cantools__cantools.0c6a7871.func_pm_ctrl_invert_if__q6ux2bx5 |
| `swe-fix-r0022-04` | 5 | `490b099580d30df6…` | python-openxml__python-docx.0cf6d71f.func_basic__betq4f8c |
| `swe-fix-r0022-05` | 6 | `a51c2c5ab1b9d611…` | oauthlib__oauthlib.1fd52536.combine_file__e7nkcn4p |
| `swe-fix-r0022-10` | 2 | `68efd36c9d7421b9…` | tobymao__sqlglot.036601ba.lm_rewrite__839odpa6 |
| `swe-fix-r0022-12` | 1 | `719c35e1040227ef…` | oauthlib__oauthlib.1fd52536.lm_rewrite__367hem7k |

</details>