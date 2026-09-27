**This round:** rank 5 · Δ vs baseline +0.016 on 6 paired instances · 0 verified.

## Round `r0023` — `5C5JKnm8M8pyn6neLqwmAKZ7DoyzJf7ZB1Mabv62LwfSEsHh`

**weight 0.0643** · score 0.0482

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0482 |
| standard error (incl. reference term) | 0.05185 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0482 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.11 | 0.00 | -0.1052 | frontier |

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
| `swe-fix-r0023-00` | 6 | `2d28876ac9083ce1…` | cantools__cantools.0c6a7871.combine_file__xnkmoktv |
| `swe-fix-r0023-01` | 1 | `fd7e177aeb981fee…` | tkrajina__gpxpy.09fc46b3.lm_rewrite__7ws8195u |
| `swe-fix-r0023-02` | 4 | `bc9e05c026d220d6…` | cantools__cantools.0c6a7871.lm_rewrite__wxmvwx55 |
| `swe-fix-r0023-03` | 5 | `8297685fbd1c28b5…` | oauthlib__oauthlib.1fd52536.combine_file__vw550k00 |
| `swe-fix-r0023-05` | 8 | `4db0625d3de22908…` | marshmallow-code__marshmallow.9716fc62.lm_rewrite__173siroi |
| `swe-fix-r0023-08` | 9 | `58fa9f7b712924b2…` | oauthlib__oauthlib.1fd52536.combine_file__ho0hneaj |

</details>