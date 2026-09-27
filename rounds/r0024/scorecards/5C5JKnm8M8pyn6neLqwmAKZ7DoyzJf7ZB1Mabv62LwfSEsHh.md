**This round:** rank 2 · Δ vs baseline +0.333 on 6 paired instances · 3 verified.

## Round `r0024` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.0964** · score 0.0794

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0794 |
| standard error (incl. reference term) | 0.058131 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0050 |
| score (mean d after the overfit and copy penalties) | +0.0794 |
| correctness gate | passed |
| Δe | api_calls +0.01 · tool_calls -0.03 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.13 | 0.00 | -0.1295 | frontier |

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
| `swe-fix-r0024-01` | 6 | `30914d83e9f33134…` | marshmallow-code__marshmallow.9716fc62.func_basic__z3csqjhj |
| `swe-fix-r0024-04` | 2 | `1076c7278c2f2319…` | cantools__cantools.0c6a7871.combine_file__cvoghn9h |
| `swe-fix-r0024-05` | 3 | `838ab0074bc258ee…` | pylint-dev__astroid.b114f6b5.func_pm_ctrl_shuffle__m2irsxet |
| `swe-fix-r0024-10` | 1 | `88318653f3875522…` | oauthlib__oauthlib.1fd52536.lm_rewrite__uja9ubfs |
| `swe-fix-r0024-11` | 5 | `113f477ceba85038…` | andialbrecht__sqlparse.e57923b3.func_basic__5g349zjv |
| `swe-fix-r0024-13` | 3 | `7fbd9d816b37f8b3…` | cantools__cantools.0c6a7871.func_pm_ctrl_invert_if__kfew88fv |

</details>