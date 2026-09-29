**This round:** not ranked · Δ vs baseline -0.167 on 6 paired instances · 0 verified.

## Round `r0033` — `5Di3Dd8PKn7uQbBc4WrzxkUqqvSL8QS3KVgCPSt3kzPE5KFb`

**weight 0.2597** · score 0.1059

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1059 |
| standard error (incl. reference term) | 0.06005 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0290 |
| score (mean d after the overfit and copy penalties) | +0.1059 |
| correctness gate | passed |
| Δe | api_calls -0.03 · tool_calls -0.09 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.21 | 0.39 | 0.181 | frontier |

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
| `swe-fix-r0033-00` | 6 | `5858d96f6f8c0a77…` | pylint-dev__astroid.b114f6b5.lm_rewrite__2tj66f5p |
| `swe-fix-r0033-01` | 4 | `0b9b050b8877b198…` | cantools__cantools.0c6a7871.combine_module__4rogard1 |
| `swe-fix-r0033-02` | 3 | `6bd31c606d9da6ee…` | pylint-dev__astroid.b114f6b5.combine_file__8crjhr3h |
| `swe-fix-r0033-04` | 2 | `719da6459c0529ee…` | python-openxml__python-docx.0cf6d71f.func_basic__875ddgth |
| `swe-fix-r0033-07` | 1 | `92175bad17cd105b…` | andialbrecht__sqlparse.e57923b3.lm_rewrite__mj94ygtt |
| `swe-fix-r0033-08` | 10 | `c6c66696fbf35076…` | python-openxml__python-docx.0cf6d71f.combine_module__bg7bc0qc |

</details>