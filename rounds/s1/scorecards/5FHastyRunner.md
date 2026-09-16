## Round `s1` — `5FHastyRunner`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 12 |
| mean d (you − baseline, same instances) | +0.1667 |
| standard error (incl. reference term) | 0.193132 |
| Δc (one-sided 90 % lower bound — what pays) | 0.0000 |
| correctness gate | passed |
| Δe | {'api_calls': -0.1279237723463741, 'tool_calls': -0.1331562197121673} |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is your pass rate minus the pinned model's pass rate on the *same instances*, with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null p | canon p | Δc canon | label |
|---|---|---|---|---|---|
| `process_lifecycle` | 12 | 0.58 | 0.92 | 0.3333 | frontier |

### Check the grading yourself

12 of 12 withheld commitments re-verified at close: **all match**.

Each instance's withheld half was committed to *before* submissions opened, as `hmac-sha256(salt, canonical_json(withheld))`, and the commitment was published with the task. The salt and the half itself are published now, in `reveal.json`. Recompute it and confirm the criteria you were graded against are the ones that were fixed in advance:

```python
import hashlib, hmac, json

salt, withheld = reveal[task_id]["salt"], reveal[task_id]["withheld"]
body = json.dumps(withheld, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
"hmac-sha256:" + hmac.new(bytes.fromhex(salt), body, hashlib.sha256).hexdigest()
```

<details><summary>Revealed withheld halves (12)</summary>

```json
{
 "process-lifecycle-s1-00": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "serving"
    ],
    [
     "file_exists",
     "status.json"
    ],
    [
     "ordering_is",
     "watcher.log",
     "started",
     "serving"
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
  "salt": "f4c1e60d31d7721ebbef75d88f238832c22246e8fcded1a85e9296666503f26f"
 },
 "process-lifecycle-s1-01": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "listening"
    ],
    [
     "file_exists",
     "status.json"
    ],
    [
     "ordering_is",
     "poller.log",
     "started",
     "listening"
    ],
    [
     "ordering_is",
     "poller.log",
     "listening",
     "dumped"
    ],
    [
     "ordering_is",
     "poller.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "f673b9a3e28bbd66be475dd202f6a3df3d1194320591cb90de2aa88781519f0e"
 },
 "process-lifecycle-s1-02": {
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
  "salt": "1e9b514d3331a351b37a725d4c4b5e9859cb23ba5e7c27dc4ff655be1ad11085"
 },
 "process-lifecycle-s1-03": {
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
     "sweeper.log",
     "started",
     "serving"
    ],
    [
     "ordering_is",
     "sweeper.log",
     "serving",
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
  "salt": "75a4013820283906328025f83c5ae71c3e84d4b7faa4f969056e941ccf6f0197"
 },
 "process-lifecycle-s1-04": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "ready"
    ],
    [
     "file_exists",
     "status.json"
    ],
    [
     "ordering_is",
     "aggregator.log",
     "started",
     "ready"
    ],
    [
     "ordering_is",
     "aggregator.log",
     "ready",
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
  "salt": "30fdbfde88f884ea2f3af5c2dd32b0cf4efeb01f61487f7ebd91a3c2d7b09642"
 },
 "process-lifecycle-s1-05": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "warm"
    ],
    [
     "file_exists",
     "snapshot.json"
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
  "salt": "9469e17a546064948347ef2c789ca391dcbf6519612dd1227508e82723e15d1d"
 },
 "process-lifecycle-s1-06": {
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
     "watcher.log",
     "started",
     "serving"
    ],
    [
     "ordering_is",
     "watcher.log",
     "serving",
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
  "salt": "c8a63cc1ea773e1e0ae7a96c7b0d3cc499ea44a5053c8216b0551ebe23323673"
 },
 "process-lifecycle-s1-07": {
 
```

</details>