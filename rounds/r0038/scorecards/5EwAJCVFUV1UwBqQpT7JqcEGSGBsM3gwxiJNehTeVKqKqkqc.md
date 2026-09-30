**This round:** not ranked · Δ vs baseline -0.056 on 6 paired instances · 0 verified.

## Round `r0038` — `5EwAJCVFUV1UwBqQpT7JqcEGSGBsM3gwxiJNehTeVKqKqkqc`

**weight 0.1610** · score 0.0926

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0926 |
| standard error (incl. reference term) | 0.051606 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0265 |
| score (mean d after the overfit and copy penalties) | +0.0926 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.13 | 0.39 | 0.2654 | frontier |

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
| `swe-fix-r0038-00` | 7 | `545994541f783fab…` | python-openxml__python-docx.0cf6d71f.func_basic__qreomw3h |
| `swe-fix-r0038-02` | 1 | `38630f5cfdf0dc4e…` | python-openxml__python-docx.0cf6d71f.func_basic__6wnvpk4z |
| `swe-fix-r0038-04` | 1 | `18d2652c8056e08d…` | pylint-dev__astroid.b114f6b5.lm_rewrite__39fdv6o4 |
| `swe-fix-r0038-05` | 8 | `4c26e59d52ecb71f…` | pylint-dev__astroid.b114f6b5.func_pm_remove_wrapper__svdnrc5i |
| `swe-fix-r0038-09` | 2 | `9625d4a31af62bf9…` | pylint-dev__astroid.b114f6b5.lm_rewrite__g7sw962m |
| `swe-fix-r0038-13` | 6 | `572428ce1fb915bc…` | python-openxml__python-docx.0cf6d71f.func_basic__f3mwwty0 |

</details>