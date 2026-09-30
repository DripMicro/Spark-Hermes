## Round `r0041` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.0081** · score 0.0060

| | |
|---|---|
| episodes | 42 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0060 |
| standard error (incl. reference term) | 0.028878 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0060 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.09 | 0.21 | 0.1199 | frontier |

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
| `swe-fix-r0041-00` | 9 | `14d678588ba7f9c0…` | pylint-dev__astroid.b114f6b5.func_pm_remove_loop__juf9p8ez |
| `swe-fix-r0041-02` | 2 | `3ed528c5a5cd775d…` | python-openxml__python-docx.0cf6d71f.func_pm_ctrl_shuffle__86qemybm |
| `swe-fix-r0041-03` | 5 | `a03b90c7633c120d…` | cantools__cantools.0c6a7871.combine_file__k6pp9ahs |
| `swe-fix-r0041-04` | 2 | `7e6d1f30100c2700…` | pylint-dev__astroid.b114f6b5.lm_rewrite__cdz0x5eu |
| `swe-fix-r0041-06` | 3 | `bec4541ac302d17a…` | pylint-dev__astroid.b114f6b5.lm_rewrite__ug21w6mo |
| `swe-fix-r0041-07` | 7 | `9efb771fec21fb9f…` | python-openxml__python-docx.0cf6d71f.combine_module__c3ajy8ka |

</details>