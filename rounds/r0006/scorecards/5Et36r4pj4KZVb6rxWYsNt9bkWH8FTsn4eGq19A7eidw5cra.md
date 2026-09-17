**This round:** rank 1 · Δ vs baseline +0.167 on 6 paired instances · 3 verified.

## Round `r0006` — `5Et36r4pj4KZVb6rxWYsNt9bkWH8FTsn4eGq19A7eidw5cra`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 17 |
| mean d (your share of checks passed − the baseline's, same instances) | -0.0000 |
| standard error (incl. reference term) | 0.144806 |
| Δc (one-sided 90 % lower bound — what pays) | 0.0000 |
| correctness gate | passed |
| Δe | api_calls -0.27 · tool_calls -0.24 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** Δ -0.000 ± 0.145 does not clear zero at 90 % — Δc = 0, nothing to pay

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 17 | 0.31 | 0.00 | -0.3109 | frontier |

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
| `swe-fix-r0006-04` | 1 | `c899b15f15fb88e8…` | python-openxml__python-docx.0cf6d71f.func_basic__cyjjip9y |
| `swe-fix-r0006-05` | 2 | `f750daa63eb84306…` | cantools__cantools.0c6a7871.func_basic__tgr298uo |
| `swe-fix-r0006-06` | 1 | `6876df8e5663d7c0…` | cantools__cantools.0c6a7871.lm_rewrite__yz71a8cb |
| `swe-fix-r0006-07` | 7 | `424e72fea33888ba…` | andialbrecht__sqlparse.e57923b3.func_basic__vrutx4jb |
| `swe-fix-r0006-08` | 2 | `49b56c800e532a10…` | andialbrecht__sqlparse.e57923b3.func_pm_remove_assign__t9s3vfqd |
| `swe-fix-r0006-11` | 1 | `82d2d427329c7239…` | tobymao__sqlglot.036601ba.func_pm_ctrl_shuffle__favd7nme |

</details>