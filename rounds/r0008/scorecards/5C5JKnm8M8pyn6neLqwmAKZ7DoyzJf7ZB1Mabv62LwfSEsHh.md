**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 1 verified.

## Round `r0008` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.0000** · score -0.0556

| | |
|---|---|
| episodes | 12 |
| mean d (your share of checks passed − the baseline's, same instances) | -0.0556 |
| standard error (incl. reference term) | 0.135048 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | -0.0556 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** at or below the baseline: Δ -0.056 ± 0.135

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.21 | 0.26 | 0.0553 | frontier |

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
| `swe-fix-r0008-01` | 1 | `f325528ba1b0f3e9…` | python-openxml__python-docx.0cf6d71f.lm_rewrite__b625srzk |
| `swe-fix-r0008-02` | 9 | `5cd4781bbedff33a…` | python-openxml__python-docx.0cf6d71f.func_pm_class_rm_funcs__mqtz5uu7 |
| `swe-fix-r0008-06` | 10 | `86eaa223fb6d0dd2…` | scanny__python-pptx.278b47b1.combine_file__t0goofvj |
| `swe-fix-r0008-07` | 10 | `da0b3bc42cc7959b…` | tobymao__sqlglot.036601ba.func_pm_ctrl_shuffle__g9vvg6xb |
| `swe-fix-r0008-12` | 1 | `e28dcc95c0fdd69f…` | pylint-dev__astroid.b114f6b5.pr_2298 |
| `swe-fix-r0008-13` | 6 | `40ac736e05e54eea…` | marshmallow-code__marshmallow.9716fc62.lm_rewrite__7es6lbv5 |

</details>