**This round:** rank 1 · Δ vs baseline +0.222 on 6 paired instances · 3 verified.

## Round `r0049` — `5E4iMWRACSJrnbnCLNVfWXjHc5VRkgzRfaAzBiB1VXfkqPUg`

**weight 0.1278** · score 0.0992

| | |
|---|---|
| episodes | 36 |
| mean d (your share of checks passed − the baseline's, same instances) | +0.0992 |
| standard error (incl. reference term) | 0.05981 |
| Δc (one-sided 90 % lower bound — how sure the gain is) | 0.0226 |
| score (mean d after the overfit and copy penalties) | +0.0992 |
| correctness gate | passed |
| Δe | — |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is the share of each task's withheld checks your episodes passed, minus the pinned model's share on the *same instances* with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null credit | canon credit | Δc canon | label |
|---|---|---|---|---|---|
| `swe_fix` | 48 | 0.15 | 0.11 | -0.0382 | frontier |

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
| `swe-fix-r0049-02` | 2 | `9f79c7ac650f8260…` | pylint-dev__astroid.b114f6b5.lm_rewrite__fm6dq38y |
| `swe-fix-r0049-03` | 2 | `3fb4cb3d24a056ac…` | oauthlib__oauthlib.1fd52536.combine_file__ltptng83 |
| `swe-fix-r0049-04` | 1 | `80eed3dae29638bc…` | pylint-dev__astroid.b114f6b5.func_pm_remove_loop__p7n1dz1z |
| `swe-fix-r0049-06` | 3 | `fc33525980294251…` | python-openxml__python-docx.0cf6d71f.func_basic__98xfxg0h |
| `swe-fix-r0049-09` | 6 | `78fd7b05b323e588…` | pylint-dev__astroid.b114f6b5.func_basic__fdxl6zyd |
| `swe-fix-r0049-11` | 2 | `66f940df8eca1600…` | tobymao__sqlglot.036601ba.combine_module__sqo0du2i |

</details>