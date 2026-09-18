**This round:** not ranked · Δ vs baseline -0.042 on 6 paired instances · 1 verified.

## Round `r0007` — `5FmyFrBu81UP5ed7vtr9DKatxdmtRDLPuduwz1yJ9eunESLC`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 23 |
| mean d (your share of checks passed − the baseline's, same instances) | -0.1413 |
| standard error (incl. reference term) | 0.117819 |
| Δc (one-sided 90 % lower bound — the score) | 0.0000 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** Δ -0.141 ± 0.118 does not clear zero at 90 % — Δc = 0, nothing to pay

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 23 | 0.32 | 0.00 | -0.3168 | frontier |

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
| `swe-fix-r0007-10` | 3 | `6a7f4088b61579a7…` | pylint-dev__astroid.b114f6b5.combine_module__8pco30g0 |
| `swe-fix-r0007-12` | 4 | `b522bad437084cdb…` | andialbrecht__sqlparse.e57923b3.lm_rewrite__8cul94v0 |
| `swe-fix-r0007-16` | 4 | `06f152eb65f87846…` | scanny__python-pptx.278b47b1.combine_file__azm9h28m |
| `swe-fix-r0007-17` | 1 | `3a82682a6379e8bd…` | pygments__pygments.27649ebb.combine_file__cx9xniyf |
| `swe-fix-r0007-18` | 3 | `9dd0984c4eec067a…` | marshmallow-code__marshmallow.9716fc62.func_basic__sjz92wyz |
| `swe-fix-r0007-21` | 2 | `eccb2375a023084c…` | pallets__jinja.ada0a9a6.pr_1918 |

</details>