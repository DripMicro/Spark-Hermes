**This round:** rank 1 · Δ vs baseline +0.200 on 5 paired instances · 1 verified.

## Round `r0004` — `5E4Rn6qxCAzsKh7Q4c6FU6DSGf2yf1LJETtDjprkzeVXiawQ`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 5 |
| mean d (your share of checks passed − the baseline's, same instances) | — |
| standard error (incl. reference term) | — |
| Δc (one-sided 90 % lower bound — what pays) | 0.0000 |
| correctness gate | not passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

> **Paid nothing:** 5 window episodes < 8

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 5 | 0.10 | 0.00 | -0.1 | unknown |

### Check the grading yourself

5 of 5 withheld commitments re-verified at close: **all match**.

Each instance's withheld half was committed to *before* submissions opened, as `hmac-sha256(salt, canonical_json(withheld))`. The commitment is in the task record — under `rounds/<id>/tasks/` when you were shown the scored tasks, under `rounds/<id>/evaluated/` when you were shown previews — and `rounds/queue.json` carried the digest of those records before the round opened. The salt and the half itself are published now, in `reveal.json`. Recompute it and confirm the criteria you were graded against are the ones that were fixed in advance:

```python
import hashlib, hmac, json
salt, withheld = reveal[task_id]["salt"], reveal[task_id]["withheld"]
body = json.dumps(withheld, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
"hmac-sha256:" + hmac.new(bytes.fromhex(salt), body, hashlib.sha256).hexdigest()
```

<details><summary>Revealed withheld halves (5) — full record in `reveal.json`</summary>

| task | withheld checks | salt | source |
|---|---|---|---|
| `swe-fix-r0004-00` | 6 | `44ea73b0636ab757…` | scanny__python-pptx.278b47b1.func_basic__f0tf9lba |
| `swe-fix-r0004-01` | 5 | `77c095f01f828e13…` | cantools__cantools.0c6a7871.func_pm_ctrl_invert_if__27pym2df |
| `swe-fix-r0004-02` | 3 | `06609743a814eb3a…` | scanny__python-pptx.278b47b1.func_basic__d8ncr3s9 |
| `swe-fix-r0004-04` | 2 | `c9b50ac36f26c02f…` | tobymao__sqlglot.036601ba.func_pm_remove_cond__xzfal0gu |
| `swe-fix-r0004-07` | 4 | `74aaa77944a10ba6…` | oauthlib__oauthlib.1fd52536.lm_rewrite__hrv1h255 |

</details>