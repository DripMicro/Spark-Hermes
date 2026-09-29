**This round:** rank 3 · Δ vs baseline +0.074 on 6 paired instances · 0 verified.

## Round `r0035` — `5EwAJCVFUV1UwBqQpT7JqcEGSGBsM3gwxiJNehTeVKqKqkqc`

**weight 0.1400** · score 0.0675

| | |
|---|---|
| episodes | 42 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0675 |
| standard error (incl. reference term) | 0.072629 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0675 |
| correctness gate | passed |
| Δe | api_calls -0.03 · tool_calls -0.08 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.19 | 0.39 | 0.1995 | frontier |

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
| `swe-fix-r0035-00` | 3 | `24a1c33ef502027c…` | pylint-dev__astroid.b114f6b5.func_basic__lgg6861n |
| `swe-fix-r0035-04` | 4 | `209d869433a776ee…` | python-openxml__python-docx.0cf6d71f.func_basic__yeh4h6e0 |
| `swe-fix-r0035-09` | 3 | `6888a15813457f0b…` | andialbrecht__sqlparse.e57923b3.combine_file__kep88kh8 |
| `swe-fix-r0035-10` | 1 | `554c772869f93f27…` | python-openxml__python-docx.0cf6d71f.func_basic__5tfxh6cc |
| `swe-fix-r0035-13` | 2 | `26de78ae3843a97b…` | python-openxml__python-docx.0cf6d71f.func_basic__w3eq8cta |
| `swe-fix-r0035-16` | 9 | `756891a03989e493…` | oauthlib__oauthlib.1fd52536.combine_file__8tij9kub |

</details>