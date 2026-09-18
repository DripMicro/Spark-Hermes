**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 1 verified.

## Round `r0008` — `5F4bmQWEFPZH9bxtrgmKtKQFFrZvsxZKfvhNmqhnc3VBku5c`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 29 |
| mean d (your share of checks passed − the baseline's, same instances) | -0.0345 |
| standard error (incl. reference term) | 0.109779 |
| Δc (one-sided 90 % lower bound — the score) | 0.0000 |
| correctness gate | passed |
| Δe | api_calls +0.15 · tool_calls +0.07 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** Δ -0.034 ± 0.110 does not clear zero at 90 % — Δc = 0, nothing to pay

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 29 | 0.29 | 0.00 | -0.2857 | frontier |

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
| `swe-fix-r0008-00` | 1 | `b2e3d0ae61941850…` | pygments__pygments.27649ebb.func_pm_class_rm_base__xfr7uzem |
| `swe-fix-r0008-01` | 3 | `08f06919461c85a4…` | tobymao__sqlglot.036601ba.func_pm_remove_assign__1vce19mw |
| `swe-fix-r0008-03` | 1 | `cfdb797804fb62af…` | marshmallow-code__marshmallow.9716fc62.lm_rewrite__pg8be73q |
| `swe-fix-r0008-04` | 3 | `58b164404b909d46…` | pygments__pygments.27649ebb.func_basic__qfq5avrb |
| `swe-fix-r0008-05` | 7 | `9a6036f40f3c8342…` | scanny__python-pptx.278b47b1.func_basic__kr879pvc |
| `swe-fix-r0008-08` | 2 | `bd8464ed7200b280…` | andialbrecht__sqlparse.e57923b3.lm_rewrite__3i3o5sl5 |

</details>