**This round:** rank 1 · Δ vs baseline +0.625 on 8 paired instances · 8 verified.

## Round `r0002` — `5FGoodOperator`

**weight 0.7668** · score 0.0366

| | |
|---|---|
| episodes | 16 |
| mean d (you − baseline, same instances) | +0.3750 |
| standard error (incl. reference term) | 0.121031 |
| Δc (one-sided 90 % lower bound — what pays) | 0.2201 |
| correctness gate | passed |
| Δe | api_calls -0.61 · tool_calls -0.79 |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is your pass rate minus the pinned model's pass rate on the *same instances*, with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null p | canon p | Δc canon | label |
|---|---|---|---|---|---|
| `process_lifecycle` | 16 | 0.62 | 0.94 | 0.3125 | frontier |

### Check the grading yourself

8 of 8 withheld commitments re-verified at close: **all match**.

Each instance's withheld half was committed to *before* submissions opened, as `hmac-sha256(salt, canonical_json(withheld))`, and the commitment was published with the task. The salt and the half itself are published now, in `reveal.json`. Recompute it and confirm the criteria you were graded against are the ones that were fixed in advance:

```python
import hashlib, hmac, json
salt, withheld = reveal[task_id]["salt"], reveal[task_id]["withheld"]
body = json.dumps(withheld, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
"hmac-sha256:" + hmac.new(bytes.fromhex(salt), body, hashlib.sha256).hexdigest()
```

<details><summary>Revealed withheld halves (8)</summary>

```json
{
 "process-lifecycle-r0002-00": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "ready"
    ],
    [
     "file_exists",
     "dump.json"
    ],
    [
     "ordering_is",
     "watcher.log",
     "started",
     "ready"
    ],
    [
     "ordering_is",
     "watcher.log",
     "ready",
     "dumped"
    ],
    [
     "ordering_is",
     "watcher.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "ff6be215c36e37af5c89c830e2e149cac1451eeccf814bbac78ce5e06bc9f937"
 },
 "process-lifecycle-r0002-01": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "listening"
    ],
    [
     "file_exists",
     "dump.json"
    ],
    [
     "ordering_is",
     "reconciler.log",
     "started",
     "listening"
    ],
    [
     "ordering_is",
     "reconciler.log",
     "listening",
     "dumped"
    ],
    [
     "ordering_is",
     "reconciler.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "c04fc3e63bb7acd45f3301f717cb7b3359606200f31210954c0141f8764d81f6"
 },
 "process-lifecycle-r0002-02": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "serving"
    ],
    [
     "file_exists",
     "snapshot.json"
    ],
    [
     "ordering_is",
     "aggregator.log",
     "started",
     "serving"
    ],
    [
     "ordering_is",
     "aggregator.log",
     "serving",
     "dumped"
    ],
    [
     "ordering_is",
     "aggregator.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "f62e65da197a94285b770cb1999167abb2d8ca8a0655bc0e2482ffc802afb746"
 },
 "process-lifecycle-r0002-03": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "serving"
    ],
    [
     "file_exists",
     "snapshot.json"
    ],
    [
     "ordering_is",
     "collector.log",
     "started",
     "serving"
    ],
    [
     "ordering_is",
     "collector.log",
     "serving",
     "dumped"
    ],
    [
     "ordering_is",
     "collector.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "c724a14f725cf90540614fc7083d6b90b072c5fca913c89d7158289d2bcd704b"
 },
 "process-lifecycle-r0002-04": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "ready"
    ],
    [
     "file_exists",
     "dump.json"
    ],
    [
     "ordering_is",
     "sweeper.log",
     "started",
     "ready"
    ],
    [
     "ordering_is",
     "sweeper.log",
     "ready",
     "dumped"
    ],
    [
     "ordering_is",
     "sweeper.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "a46c45981c01a148958bc6db1e107b09f19dbaf64598ead23ec724958d9951d9"
 },
 "process-lifecycle-r0002-05": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "warm"
    ],
    [
     "file_exists",
     "dump.json"
    ],
    [
     "ordering_is",
     "reconciler.log",
     "started",
     "warm"
    ],
    [
     "ordering_is",
     "reconciler.log",
     "warm",
     "dumped"
    ],
    [
     "ordering_is",
     "reconciler.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "9b7d4475ef70c707b6e2b73d7d2c828f099fb385b15b72fd7c5757e053e86102"
 },
 "process-lifecycle-r0002-06": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "listening"
    ],
    [
     "file_exists",
     "dump.json"
    ],
    [
     "ordering_is",
     "sweeper.log",
     "started",
     "listening"
    ],
    [
     "ordering_is",
     "sweeper.log",
     "listening",
     "dumped"
    ],
    [
     "ordering_is",
     "sweeper.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "cc82
```

</details>