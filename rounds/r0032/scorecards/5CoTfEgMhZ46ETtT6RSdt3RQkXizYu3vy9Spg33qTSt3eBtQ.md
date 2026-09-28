**This round:** rank 4 · Δ vs baseline +0.056 on 6 paired instances · 1 verified.

## Round `r0032` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.2447** · score 0.1383

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1383 |
| standard error (incl. reference term) | 0.065925 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0539 |
| score (mean d after the overfit and copy penalties) | +0.1383 |
| correctness gate | passed |
| Δe | api_calls -0.32 · tool_calls -0.34 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.18 | 0.39 | 0.213 | frontier |

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
| `swe-fix-r0032-00` | 7 | `0f79ebee1f279436…` | pylint-dev__astroid.b114f6b5.func_basic__hx27usa7 |
| `swe-fix-r0032-02` | 1 | `2c7d028608aae007…` | andialbrecht__sqlparse.e57923b3.lm_rewrite__0qd7z9ez |
| `swe-fix-r0032-03` | 3 | `65d22136ddbd7bda…` | python-openxml__python-docx.0cf6d71f.func_basic__70gu88dv |
| `swe-fix-r0032-04` | 2 | `f5908a685391238c…` | tobymao__sqlglot.036601ba.combine_module__o0tnv74o |
| `swe-fix-r0032-08` | 2 | `7cf6777bf8cbeadc…` | andialbrecht__sqlparse.e57923b3.func_pm_ctrl_shuffle__r8lfv07j |
| `swe-fix-r0032-10` | 7 | `c317394dea7cca7d…` | python-openxml__python-docx.0cf6d71f.combine_file__m25dyofy |

</details>