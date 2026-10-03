**This round:** rank 3 · Δ vs baseline +0.100 on 6 paired instances · 2 verified.

## Round `r0051` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.2215** · score 0.1033

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1033 |
| standard error (incl. reference term) | 0.060355 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0260 |
| score (mean d after the overfit and copy penalties) | +0.1033 |
| correctness gate | passed |
| Δe | api_calls +0.00 · tool_calls -0.07 |
| overfit rate | 0.00 |
| disqualified episodes | 1 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.20 | 0.11 | -0.0924 | frontier |

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
| `swe-fix-r0051-00` | 3 | `e00c1461b278f42c…` | cantools__cantools.0c6a7871.func_basic__foufnnpt |
| `swe-fix-r0051-03` | 3 | `3f32b45c8abcd87b…` | pylint-dev__astroid.b114f6b5.combine_file__1i4n2czq |
| `swe-fix-r0051-04` | 1 | `a2f13050d8d14f77…` | cantools__cantools.0c6a7871.func_basic__dm0p2o1m |
| `swe-fix-r0051-07` | 5 | `876246f8bc158a58…` | oauthlib__oauthlib.1fd52536.lm_rewrite__uql5tgba |
| `swe-fix-r0051-09` | 5 | `c028a4dba0ffbbb4…` | andialbrecht__sqlparse.e57923b3.lm_rewrite__66akbl4j |
| `swe-fix-r0051-11` | 1 | `b8cd71c527ed6bdd…` | andialbrecht__sqlparse.e57923b3.func_basic__7p73klsa |

</details>