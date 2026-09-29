**This round:** rank 1 · Δ vs baseline +0.208 on 6 paired instances · 1 verified.

## Round `r0034` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.2078** · score 0.0880

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0880 |
| standard error (incl. reference term) | 0.069377 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0880 |
| correctness gate | passed |
| Δe | api_calls -0.20 · tool_calls -0.28 |
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
| `swe-fix-r0034-01` | 1 | `bee1b2050c177f51…` | tobymao__sqlglot.036601ba.lm_rewrite__mr2bycj7 |
| `swe-fix-r0034-02` | 4 | `73b22488cb35c622…` | cantools__cantools.0c6a7871.lm_rewrite__zjpnfas0 |
| `swe-fix-r0034-06` | 4 | `07632435a0cb4064…` | tobymao__sqlglot.036601ba.func_pm_remove_assign__ads3ucxx |
| `swe-fix-r0034-11` | 4 | `7e6aade10eab465b…` | tobymao__sqlglot.036601ba.func_pm_remove_cond__8ipu2ysq |
| `swe-fix-r0034-14` | 1 | `b83026cea506a95f…` | tobymao__sqlglot.036601ba.lm_rewrite__mchmm6b4 |
| `swe-fix-r0034-16` | 2 | `483b7f1cfab571de…` | pylint-dev__astroid.b114f6b5.func_basic__q49heztm |

</details>