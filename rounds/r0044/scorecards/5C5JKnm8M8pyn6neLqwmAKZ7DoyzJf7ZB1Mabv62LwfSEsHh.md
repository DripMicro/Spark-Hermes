**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 1 verified.

## Round `r0044` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.1537** · score 0.1012

| | |
|---|---|
| episodes | 42 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1012 |
| standard error (incl. reference term) | 0.061474 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0225 |
| score (mean d after the overfit and copy penalties) | +0.1012 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 1 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.13 | 0.21 | 0.0736 | frontier |

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
| `swe-fix-r0044-01` | 1 | `f14426d19b781ed2…` | tkrajina__gpxpy.09fc46b3.lm_rewrite__6vk0xepl |
| `swe-fix-r0044-06` | 9 | `edde9f070b597ba8…` | cantools__cantools.0c6a7871.combine_file__jzfns9hi |
| `swe-fix-r0044-11` | 2 | `1f90437f4ab20c0f…` | python-openxml__python-docx.0cf6d71f.func_basic__y0cho4r1 |
| `swe-fix-r0044-12` | 6 | `26fbcee41ce45fb2…` | cantools__cantools.0c6a7871.combine_file__01jft1mj |
| `swe-fix-r0044-14` | 6 | `e189706fe0b4fc44…` | tobymao__sqlglot.036601ba.lm_rewrite__ng2hotsp |
| `swe-fix-r0044-15` | 1 | `ed36180bee284f4a…` | andialbrecht__sqlparse.e57923b3.func_basic__4gsssbwq |

</details>