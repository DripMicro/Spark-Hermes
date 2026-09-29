**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 0 verified.

## Round `r0036` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.0000** · score -0.0278

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | -0.0278 |
| standard error (incl. reference term) | 0.049459 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | -0.0278 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** at or below the baseline: Δ -0.028 ± 0.049

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.16 | 0.39 | 0.2366 | frontier |

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
| `swe-fix-r0036-00` | 7 | `3bc561b8ce97f3be…` | pylint-dev__astroid.b114f6b5.combine_file__muvsbbrj |
| `swe-fix-r0036-01` | 5 | `f45da17f906572a2…` | oauthlib__oauthlib.1fd52536.combine_file__y7avru6f |
| `swe-fix-r0036-04` | 1 | `e0a3ebb7576c8355…` | oauthlib__oauthlib.1fd52536.lm_rewrite__btci6v9o |
| `swe-fix-r0036-07` | 1 | `1d46198bda528a34…` | pylint-dev__astroid.b114f6b5.func_pm_remove_cond__2enckjr5 |
| `swe-fix-r0036-09` | 2 | `af05cd0529349688…` | pylint-dev__astroid.b114f6b5.combine_file__u8lxqjtu |
| `swe-fix-r0036-10` | 4 | `cf82afe91dd1cf9c…` | pylint-dev__astroid.b114f6b5.combine_file__wsiokh1r |

</details>