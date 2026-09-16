## Round `r0001` — `5FGoodOperator`

**weight 0.0000** · scored nothing this round

| | |
|---|---|
| episodes | 8 |
| mean d (you − baseline, same instances) | +0.1250 |
| standard error (incl. reference term) | 0.116927 |
| Δc (one-sided 90 % lower bound — what pays) | 0.0000 |
| correctness gate | passed |
| Δe | {'api_calls': -0.4257653127400949, 'tool_calls': -0.7342205144229418} |
| overfit rate | 0.00 |
| disqualified episodes | 0 |

`mean d` is your pass rate minus the pinned model's pass rate on the *same instances*, with no strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of that difference, so beating the baseline on average is not enough to be *paid* for beating it.

### The baseline you were measured against

| family | null n | null p | canon p | Δc canon | label |
|---|---|---|---|---|---|
| `process_lifecycle` | 8 | 0.88 | 0.88 | 0.0 | frontier |

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
 "process-lifecycle-r0001-00": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "serving"
    ],
    [
     "file_exists",
     "dump.json"
    ],
    [
     "ordering_is",
     "indexer.log",
     "started",
     "serving"
    ],
    [
     "ordering_is",
     "indexer.log",
     "serving",
     "dumped"
    ],
    [
     "ordering_is",
     "indexer.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "22f97279f03460536994a2fe33365f96bbfb960251d549fcd83db34828150e87"
 },
 "process-lifecycle-r0001-01": {
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
     "collector.log",
     "started",
     "serving"
    ]
   ]
  },
  "salt": "e60c7d5f7b144d7939a4d5bd0fa15249b638c5f09bf9fe627cd3611ba1bd6651"
 },
 "process-lifecycle-r0001-02": {
  "withheld": {
   "predicates": [
    [
     "file_exists",
     "serving"
    ],
    [
     "file_exists",
     "state.json"
    ],
    [
     "ordering_is",
     "reconciler.log",
     "started",
     "serving"
    ],
    [
     "ordering_is",
     "reconciler.log",
     "serving",
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
  "salt": "3889064089a423b34a624c9c7dba2a60540a7577359396546524b8df9edd2b84"
 },
 "process-lifecycle-r0001-03": {
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
  "salt": "2cbfd7513ff2ef7e0ba90f365be99410bde69bf9b745acb979d4a7be8b931db4"
 },
 "process-lifecycle-r0001-04": {
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
     "indexer.log",
     "started",
     "warm"
    ],
    [
     "ordering_is",
     "indexer.log",
     "warm",
     "dumped"
    ],
    [
     "ordering_is",
     "indexer.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "2a2694d48bc78bae3dfb8792e4de284cef3e2d5624109801c8d4b9525de866fd"
 },
 "process-lifecycle-r0001-05": {
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
     "indexer.log",
     "started",
     "warm"
    ],
    [
     "ordering_is",
     "indexer.log",
     "warm",
     "dumped"
    ],
    [
     "ordering_is",
     "indexer.log",
     "dumped",
     "stopped"
    ],
    [
     "custom",
     "state_came_from_the_running_server"
    ]
   ]
  },
  "salt": "86554cb7c5bc64049ea3b1ee8ab8a8afe33cf6ecd2912e7208842a36777d0aef"
 },
 "process-lifecycle-r0001-06": {
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
  "salt": "b4599c451783c6d61dd7e0671756b9a24e9626ed0fa9aac7661299c97b7d046b"
 },
 "process-lifecycle-r0001-07": {
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
     "
```

</details>