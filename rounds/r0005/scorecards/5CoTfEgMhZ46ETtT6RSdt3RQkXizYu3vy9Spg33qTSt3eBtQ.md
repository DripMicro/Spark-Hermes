**This round:** not ranked · Δ vs baseline +0.000 on 6 paired instances · 0 verified.

## Round `r0005` — `5CoTfEgMhZ46ETtT6RSdt3RQkXizYu3vy9Spg33qTSt3eBtQ`

**weight 0.4020** · score 0.1889

| | |
|---|---|
| episodes | 30 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.1889 |
| standard error (incl. reference term) | 0.078187 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0888 |
| score (mean d after the overfit and copy penalties) | +0.1889 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 30 | 0.16 | — | — | frontier |

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
| `swe-fix-r0005-00` | 1 | `5c1c323d8947d6c9…` | pylint-dev__astroid.b114f6b5.func_pm_remove_loop__5rcm3eey |
| `swe-fix-r0005-03` | 7 | `c679d07ba655b05c…` | cantools__cantools.0c6a7871.combine_file__2brlcts5 |
| `swe-fix-r0005-05` | 7 | `248dde730765526a…` | pylint-dev__astroid.b114f6b5.func_pm_remove_wrapper__94c7ttqp |
| `swe-fix-r0005-08` | 9 | `5f70bb42b1edb497…` | python-openxml__python-docx.0cf6d71f.combine_module__gexknq9z |
| `swe-fix-r0005-10` | 2 | `5d15ca9b91b9521b…` | python-openxml__python-docx.0cf6d71f.lm_rewrite__wxfm88xy |
| `swe-fix-r0005-11` | 4 | `8b2be3e794f7c1c3…` | cantools__cantools.0c6a7871.func_basic__oi5gz2e8 |

</details>