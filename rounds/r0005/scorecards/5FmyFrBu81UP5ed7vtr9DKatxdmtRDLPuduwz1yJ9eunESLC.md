**This round:** not ranked · Δ vs baseline -0.417 on 6 paired instances · 0 verified.

## Round `r0005` — `5FmyFrBu81UP5ed7vtr9DKatxdmtRDLPuduwz1yJ9eunESLC`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 11 |
| mean d (your share of checks passed − the baseline's, same instances) | -0.2727 |
| standard error (incl. reference term) | 0.117895 |
| Δc (one-sided 90 % lower bound — what pays) | 0.0000 |
| correctness gate | not passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** below the baseline: Δ -0.273 ± 0.118

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 11 | 0.27 | 0.00 | -0.2727 | frontier |

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
| `swe-fix-r0005-01` | 3 | `70277605b7f48b0c…` | python-openxml__python-docx.0cf6d71f.func_basic__mbk3mihv |
| `swe-fix-r0005-03` | 2 | `1498ce0b6330bdc4…` | oauthlib__oauthlib.1fd52536.lm_rewrite__ymz6voe4 |
| `swe-fix-r0005-04` | 4 | `25b66e0857d25bcc…` | tobymao__sqlglot.036601ba.func_pm_ctrl_invert_if__450o3cgn |
| `swe-fix-r0005-05` | 1 | `895c0d1a0ffa1ef8…` | tobymao__sqlglot.036601ba.func_pm_remove_cond__m7o1jzpd |
| `swe-fix-r0005-07` | 9 | `c8af6caa1af5551a…` | pallets__jinja.ada0a9a6.lm_rewrite__ffkd8o8c |
| `swe-fix-r0005-09` | 2 | `e2279ac847a2f93d…` | pylint-dev__astroid.b114f6b5.func_pm_remove_cond__w3kxiukf |

</details>