**This round:** rank 3 · Δ vs baseline +0.194 on 6 paired instances · 1 verified.

## Round `r0040` — `5Di3Dd8PKn7uQbBc4WrzxkUqqvSL8QS3KVgCPSt3kzPE5KFb`

**weight 0.2199** · score 0.1128

| | |
|---|---|
| episodes | 48 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1128 |
| standard error (incl. reference term) | 0.05985 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0362 |
| score (mean d after the overfit and copy penalties) | +0.1128 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.11 | 0.21 | 0.0935 | frontier |

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
| `swe-fix-r0040-00` | 4 | `96fc775268e56642…` | pylint-dev__astroid.b114f6b5.lm_rewrite__08v06c41 |
| `swe-fix-r0040-01` | 4 | `4af2f03142c5d715…` | oauthlib__oauthlib.1fd52536.combine_file__6za0pzef |
| `swe-fix-r0040-02` | 9 | `85780b1aaecdc283…` | cantools__cantools.0c6a7871.combine_file__x23bjyg5 |
| `swe-fix-r0040-05` | 3 | `694a9765fb78570a…` | cantools__cantools.0c6a7871.combine_module__94v6dlji |
| `swe-fix-r0040-09` | 1 | `9a6e245c476d998b…` | cantools__cantools.0c6a7871.combine_file__j2y9q08y |
| `swe-fix-r0040-12` | 2 | `2f85b02233427ecf…` | cantools__cantools.0c6a7871.func_basic__ln0ffhyx |

</details>