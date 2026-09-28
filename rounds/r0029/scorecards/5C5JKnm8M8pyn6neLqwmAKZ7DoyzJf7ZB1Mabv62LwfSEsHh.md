**This round:** not ranked · Δ vs baseline -0.278 on 6 paired instances · 0 verified.

## Round `r0029` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.0000** · score -0.0420

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | -0.0420 |
| standard error (incl. reference term) | 0.062296 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | -0.0420 |
| correctness gate | passed |
| Δe | api_calls +0.09 · tool_calls +0.11 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** at or below the baseline: Δ -0.042 ± 0.062

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.22 | 0.00 | -0.2159 | frontier |

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
| `swe-fix-r0029-05` | 3 | `2cd2ac78978b1e6f…` | pylint-dev__astroid.b114f6b5.func_pm_ctrl_shuffle__f6xdhaus |
| `swe-fix-r0029-07` | 2 | `5eb277a3cf3f51c0…` | tobymao__sqlglot.036601ba.func_pm_ctrl_shuffle__0n71k5az |
| `swe-fix-r0029-08` | 2 | `f14414f3ee2ac8be…` | pylint-dev__astroid.b114f6b5.pr_2438 |
| `swe-fix-r0029-09` | 6 | `c37d5399b38d35a2…` | tkrajina__gpxpy.09fc46b3.func_pm_remove_assign__j9zi25pm |
| `swe-fix-r0029-11` | 2 | `246f19ce89029d1a…` | pylint-dev__astroid.b114f6b5.func_basic__omgp8465 |
| `swe-fix-r0029-14` | 6 | `1fab0e42b2064563…` | python-openxml__python-docx.0cf6d71f.func_basic__9afx1rcm |

</details>