**This round:** rank 1 · Δ vs baseline +0.167 on 6 paired instances · 2 verified.

## Round `r0030` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.3483** · score 0.1576

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1576 |
| standard error (incl. reference term) | 0.069522 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0687 |
| score (mean d after the overfit and copy penalties) | +0.1576 |
| correctness gate | passed |
| Δe | api_calls -0.06 · tool_calls -0.03 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.17 | 0.00 | -0.1742 | frontier |

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
| `swe-fix-r0030-00` | 4 | `8d5ae1a2e453cf9e…` | python-openxml__python-docx.0cf6d71f.func_basic__623koi2p |
| `swe-fix-r0030-02` | 2 | `5e82cfbab51c354c…` | python-openxml__python-docx.0cf6d71f.func_basic__c3dfcyho |
| `swe-fix-r0030-03` | 1 | `0c623c7ec8905c1c…` | python-openxml__python-docx.0cf6d71f.combine_file__t8xl8zaw |
| `swe-fix-r0030-05` | 1 | `a9c8c18e555c6eca…` | tobymao__sqlglot.036601ba.func_pm_remove_assign__y0w2g6d1 |
| `swe-fix-r0030-10` | 2 | `577a8655bc287d9b…` | cantools__cantools.0c6a7871.lm_rewrite__daqnkxxy |
| `swe-fix-r0030-11` | 1 | `4bd45a1d7f1935cd…` | pylint-dev__astroid.b114f6b5.func_basic__eadr5u0i |

</details>