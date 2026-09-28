**This round:** not ranked · Δ vs baseline -0.296 on 6 paired instances · 0 verified.

## Round `r0028` — `5EwAJCVFUV1UwBqQpT7JqcEGSGBsM3gwxiJNehTeVKqKqkqc`

**weight 0.1404** · score 0.0644

| | |
|---|---|
| episodes | 36 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0644 |
| standard error (incl. reference term) | 0.076846 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0644 |
| correctness gate | passed |
| Δe | api_calls -0.11 · tool_calls -0.13 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.19 | 0.00 | -0.1881 | frontier |

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
| `swe-fix-r0028-00` | 9 | `037248c11e396aa2…` | cantools__cantools.0c6a7871.lm_rewrite__dfvm2n5z |
| `swe-fix-r0028-01` | 1 | `a59c2b411b6163d0…` | pylint-dev__astroid.b114f6b5.pr_2263 |
| `swe-fix-r0028-02` | 9 | `76194689f8de2b9e…` | cantools__cantools.0c6a7871.combine_module__cjsnnrd5 |
| `swe-fix-r0028-03` | 7 | `a5236ed705e70951…` | cantools__cantools.0c6a7871.combine_file__wax5fvgt |
| `swe-fix-r0028-04` | 9 | `e76c2b17dc854013…` | pylint-dev__astroid.b114f6b5.func_basic__l29ig3k1 |
| `swe-fix-r0028-06` | 10 | `b949eee166db87c0…` | python-openxml__python-docx.0cf6d71f.func_basic__oydbgg2e |

</details>