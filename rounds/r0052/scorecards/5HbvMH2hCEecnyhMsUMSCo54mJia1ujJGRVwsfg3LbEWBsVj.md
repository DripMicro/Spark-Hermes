**This round:** rank 6 · Δ vs baseline +0.083 on 6 paired instances · 4 verified.

## Round `r0052` — `5HbvMH2hCEecnyhMsUMSCo54mJia1ujJGRVwsfg3LbEWBsVj`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 12 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0000 |
| standard error (incl. reference term) | 0.061546 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0000 |
| correctness gate | passed |
| Δe | api_calls -0.42 · tool_calls -0.02 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** at or below the baseline: Δ +0.000 ± 0.062

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.25 | 0.11 | -0.1354 | frontier |

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
| `swe-fix-r0052-02` | 1 | `3c33a689ddbc66db…` | pylint-dev__astroid.b114f6b5.pr_2589 |
| `swe-fix-r0052-03` | 2 | `daa9f4921691d682…` | marshmallow-code__marshmallow.9716fc62.func_basic__xnxp84t9 |
| `swe-fix-r0052-04` | 5 | `3d1ae65168ad996c…` | python-openxml__python-docx.0cf6d71f.combine_file__o5i4caut |
| `swe-fix-r0052-05` | 1 | `a268767e1d089061…` | tobymao__sqlglot.036601ba.func_pm_ctrl_shuffle__3dny185x |
| `swe-fix-r0052-06` | 2 | `21a81a3f0584ffc4…` | tobymao__sqlglot.036601ba.func_pm_remove_loop__alg83sy1 |
| `swe-fix-r0052-09` | 5 | `661d2235120d3bd4…` | cantools__cantools.0c6a7871.func_pm_remove_cond__1adlrus6 |

</details>