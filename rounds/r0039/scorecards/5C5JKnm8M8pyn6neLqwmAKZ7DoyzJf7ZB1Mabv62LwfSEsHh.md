**This round:** rank 3 · Δ vs baseline +0.083 on 6 paired instances · 1 verified.

## Round `r0039` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.0000** · score -0.0191

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | -0.0191 |
| standard error (incl. reference term) | 0.031798 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | -0.0191 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** at or below the baseline: Δ -0.019 ± 0.032

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.15 | 0.39 | 0.2394 | frontier |

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
| `swe-fix-r0039-03` | 1 | `e62d31a6aff48a74…` | tobymao__sqlglot.036601ba.func_pm_remove_cond__vbedhpfx |
| `swe-fix-r0039-04` | 4 | `7aba218859b19a68…` | tobymao__sqlglot.036601ba.func_pm_ctrl_invert_if__ki6n3oo4 |
| `swe-fix-r0039-08` | 2 | `16dd689d580058f9…` | pylint-dev__astroid.b114f6b5.pr_2562 |
| `swe-fix-r0039-13` | 4 | `52c6ce3563ffc4c8…` | cantools__cantools.0c6a7871.func_pm_ctrl_invert_if__x6tyea1c |
| `swe-fix-r0039-14` | 4 | `40c3715f642c3c79…` | cantools__cantools.0c6a7871.lm_rewrite__7d7x3i7n |
| `swe-fix-r0039-15` | 3 | `bdc3fd0bee64a7bf…` | oauthlib__oauthlib.1fd52536.lm_rewrite__0pmptnff |

</details>