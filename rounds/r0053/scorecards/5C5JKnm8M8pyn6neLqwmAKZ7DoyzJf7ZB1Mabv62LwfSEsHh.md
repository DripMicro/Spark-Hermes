**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 5 verified.

## Round `r0053` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.1694** · score 0.0590

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0590 |
| standard error (incl. reference term) | 0.047299 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0590 |
| correctness gate | passed |
| Δe | api_calls -0.25 · tool_calls -0.05 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.35 | 0.11 | -0.2396 | frontier |

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
| `swe-fix-r0053-00` | 1 | `4b08e883586cbdc4…` | oauthlib__oauthlib.1fd52536.lm_rewrite__6b1endl1 |
| `swe-fix-r0053-02` | 3 | `d84afba9b95b6f0d…` | oauthlib__oauthlib.1fd52536.combine_module__5shhy7iu |
| `swe-fix-r0053-03` | 1 | `9cb54929d9e28fa5…` | oauthlib__oauthlib.1fd52536.combine_file__u0jblbrb |
| `swe-fix-r0053-05` | 5 | `b7facc7ad5e5a070…` | pylint-dev__astroid.b114f6b5.func_pm_remove_wrapper__nrglkq03 |
| `swe-fix-r0053-06` | 4 | `70e14bc1b7c9362d…` | pylint-dev__astroid.b114f6b5.pr_2598 |
| `swe-fix-r0053-07` | 1 | `04e99d055ef03523…` | pylint-dev__astroid.b114f6b5.func_basic__3lcv6a6y |

</details>