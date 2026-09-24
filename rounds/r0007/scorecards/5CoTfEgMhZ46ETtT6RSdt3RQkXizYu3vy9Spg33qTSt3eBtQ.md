**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 1 verified.

## Round `r0007` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.2534** · score 0.1349

| | |
|---|---|
| episodes | 42 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1349 |
| standard error (incl. reference term) | 0.05715 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0618 |
| score (mean d after the overfit and copy penalties) | +0.1349 |
| correctness gate | passed |
| Δe | api_calls -0.90 · tool_calls -1.00 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 42 | 0.20 | — | — | frontier |

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
| `swe-fix-r0007-05` | 7 | `9f9b3240656514c0…` | python-openxml__python-docx.0cf6d71f.combine_file__r6o6cghw |
| `swe-fix-r0007-06` | 8 | `32f3e11ec6ea994b…` | cantools__cantools.0c6a7871.combine_module__56wsz9nm |
| `swe-fix-r0007-10` | 8 | `48ab122515726eb9…` | tobymao__sqlglot.036601ba.func_pm_ctrl_shuffle__1krctpib |
| `swe-fix-r0007-11` | 7 | `6170107327cf70c4…` | cantools__cantools.0c6a7871.combine_file__h8qxxgob |
| `swe-fix-r0007-12` | 1 | `4101556eb5ec7053…` | oauthlib__oauthlib.1fd52536.func_basic__j4skbqpn |
| `swe-fix-r0007-14` | 6 | `1c7e1fa8c6d2017a…` | cantools__cantools.0c6a7871.func_basic__ibge568f |

</details>