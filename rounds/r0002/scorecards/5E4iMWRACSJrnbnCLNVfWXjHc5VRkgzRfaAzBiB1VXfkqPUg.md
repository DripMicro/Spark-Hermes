**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 1 verified.

## Round `r0002` — `5E4iMWRACSJrnbnCLNVfWXjHc5VRkgzRfaAzBiB1VXfkqPUg`

**weight 0.0833** · score 0.0556

| | |
|---|---|
| episodes | 12 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0556 |
| standard error (incl. reference term) | 0.182728 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0556 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 12 | 0.17 | — | — | frontier |

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
| `swe-fix-r0002-01` | 4 | `fe600889a90d66e5…` | tobymao__sqlglot.036601ba.lm_rewrite__9lfd11cr |
| `swe-fix-r0002-02` | 2 | `f823d94e1effe1f8…` | tobymao__sqlglot.036601ba.combine_file__pbfl37if |
| `swe-fix-r0002-03` | 1 | `92a1d1b5ae160cf7…` | cantools__cantools.0c6a7871.lm_rewrite__9hi2rn7q |
| `swe-fix-r0002-06` | 6 | `dba95eb400901fbc…` | python-openxml__python-docx.0cf6d71f.combine_file__9cpzf1ms |
| `swe-fix-r0002-07` | 3 | `501d03dde7e9ef50…` | python-openxml__python-docx.0cf6d71f.func_pm_class_rm_funcs__4uigqgap |
| `swe-fix-r0002-08` | 5 | `381c7cdcd98aa018…` | python-openxml__python-docx.0cf6d71f.combine_module__g6ptzfwa |

</details>