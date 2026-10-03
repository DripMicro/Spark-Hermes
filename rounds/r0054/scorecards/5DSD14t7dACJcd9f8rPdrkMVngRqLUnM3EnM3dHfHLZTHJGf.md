**This round:** rank 4 · Δ vs baseline +0.056 on 6 paired instances · 3 verified.

## Round `r0054` — `5DSD14t7dACJcd9f8rPdrkMVngRqLUnM3EnM3dHfHLZTHJGf`

**weight 0.0450** · score 0.0181

| | |
|---|---|
| episodes | 24 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0181 |
| standard error (incl. reference term) | 0.055712 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0000 |
| score (mean d after the overfit and copy penalties) | +0.0181 |
| correctness gate | passed |
| Δe | api_calls -0.17 · tool_calls +0.00 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.41 | 0.11 | -0.3021 | frontier |

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
| `swe-fix-r0054-01` | 1 | `89853760a09162b9…` | pylint-dev__astroid.b114f6b5.func_basic__ik5ian7i |
| `swe-fix-r0054-03` | 6 | `829e38fca725ff03…` | python-openxml__python-docx.0cf6d71f.func_pm_ctrl_shuffle__3vq5blxh |
| `swe-fix-r0054-04` | 3 | `2a1221b8f2439dc1…` | pylint-dev__astroid.b114f6b5.lm_rewrite__d0ail4ie |
| `swe-fix-r0054-06` | 9 | `ea080421239a320e…` | python-openxml__python-docx.0cf6d71f.func_pm_ctrl_invert_if__imzmsc3f |
| `swe-fix-r0054-11` | 8 | `a5daf498b4f6413d…` | pylint-dev__astroid.b114f6b5.func_pm_remove_cond__mjm24ooq |
| `swe-fix-r0054-12` | 3 | `b4409c0b88defafb…` | cantools__cantools.0c6a7871.func_pm_ctrl_invert_if__qvsanhqw |

</details>