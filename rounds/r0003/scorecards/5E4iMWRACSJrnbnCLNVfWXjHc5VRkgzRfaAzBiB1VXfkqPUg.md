**This round:** rank 1 · Δ vs baseline +0.133 on 6 paired instances · 1 verified.

## Round `r0003` — `5E4iMWRACSJrnbnCLNVfWXjHc5VRkgzRfaAzBiB1VXfkqPUg`

**weight 0.1536** · score 0.0815

| | |
|---|---|
| episodes | 18 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0815 |
| standard error (incl. reference term) | 0.127379 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0815 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 18 | 0.21 | — | — | frontier |

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
| `swe-fix-r0003-01` | 5 | `06cd50ed9a78d46d…` | pylint-dev__astroid.b114f6b5.combine_file__8v055hvx |
| `swe-fix-r0003-02` | 4 | `50e3b3dd7622b115…` | tkrajina__gpxpy.09fc46b3.func_pm_op_change__8klzpvun |
| `swe-fix-r0003-07` | 5 | `936305e041d17cfc…` | oauthlib__oauthlib.1fd52536.func_basic__v5uhrs3v |
| `swe-fix-r0003-10` | 9 | `d014e68a139c18d9…` | pylint-dev__astroid.b114f6b5.func_pm_remove_assign__0cjyib37 |
| `swe-fix-r0003-13` | 1 | `cdc79b0f2dfe1582…` | cantools__cantools.0c6a7871.lm_rewrite__gqgbjex3 |
| `swe-fix-r0003-15` | 2 | `a0e0375b669d7cbe…` | scanny__python-pptx.278b47b1.func_pm_class_rm_funcs__m8oxfyr2 |

</details>