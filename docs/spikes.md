# Verification spikes (requirements §17) — raw results

Host `91.224.44.223:50199`, RTX 5090 32 GB. Pins: `docs/pins.md`.

| Spike | Result | Evidence |
|---|---|---|
| A0 | **built** | `hermes-base:pin` = `sha256:49224eca…` (system Python 3.12; `import run_agent` ok as uid 1000). First build failed: `.python-version`=3.11 made uv download a managed interpreter under `/root`, unreadable by uid 1000 — fixed with `UV_PYTHON_DOWNLOADS=never --python /usr/local/bin/python3`. |
| V1 | **pass** | `POST /v1/chat/completions` with `tools` → `finish_reason: tool_calls`, `tool_calls[0].function.arguments` = `{"command":"ls -la"}`, id `call_…`. `usage.prompt_tokens_details.cached_tokens` present (prefix caching live). No reasoning-token field → `output_tokens` stays unrewarded (FR-SCR-4). |
| V2 | **pass** (2nd attempt) | 1st attempt: Hermes `_enforce_minimum_context` refused a 32,768 window ("minimum 64,000"). Engine restarted at `CTX=65536` (healthy in 15 s; 23 GB used). 2nd attempt: `posix-report-spike-07`, 5 LLM calls, 4 tool calls, **28 s**, published `[true, true]`, withheld `[true]` → verified success; the agent wrote a POSIX `report.sh` and self-tested it with `sh`. `providers.custom.type` is an unknown key at the pin (ignored). |
| V2b | (a) chosen | Host-path bind mounts do not work on this host (overlay root): runner I/O must use stdin tar-in + `docker cp`/exec tar-out, not `-v host:container`. Topology (a) confirmed workable; (b) not attempted (socket escape). |
| V3 | **pass** (SOUL · skills index · lazy body · reference via `skill_view`) | `_build_system_prompt()` (8,341 chars) contains the `SOUL.md` sentinel with `load_soul_identity=True, skip_context_files=False` → the miner's SOUL is in the live prompt programmatically. `result["messages"]` carries **no** system message and the converter emits its own system turn, so neither can be used to check the prompt — inspect `agent._build_system_prompt()`. The skill (`/home/hermes/skills/posix-shell`) was **not** listed in the prompt with `enabled_toolsets=[terminal, file]`; With `enabled_toolsets` including `skills` the index renders (`posix-shell: How to write shell scripts that run under dash, with a re...` — descriptions are **truncated to ~60 chars** in the index; tell miners) and the skill body is absent from the prompt (lazy). Toolset ids at the pin recorded in spec §5.3; `skill_view`/`skill_manage` share the `skills` toolset; `skills.write_approval: true` **stages** writes (no hang) so `skill_manage` is neutralised headless. Episode solved the task: 7 calls, 8 tool calls, 65 s. **V3b**: with the `skills` toolset enabled, `_build_system_prompt()` = 10,054 chars with SOUL + `posix-shell` listed; the agent made 1 `skill_view` call and the tool result contained the reference sentinel; task solved, 11 calls, 43 s. |
| V4 | **pass, with two export rules** | `_convert_to_trajectory_format(messages, user_query, completed)` → list of `{from, value}`: roles system/human/gpt/tool; **7/7 gpt turns have `<think>`**; `<tool_call>` JSON in gpt; `<tool_response>` in tool. Its system turn (13,074 chars) is the generic *"You are a function calling AI model… <tools>"* prompt — **no SOUL, no skills index**, i.e. not what deployment sees (Hermes' built prompt, 8–10K chars). Export therefore (1) replaces the system turn with the NULL-surface `agent._build_system_prompt()` captured at the pin and passes tool schemas via the row's `tools` field, and (2) in `keep` mode re-inserts the miner's skills index (the converter drops it). |
| B1/B2 | **boundary closed** | `net-up.sh` builds `sh-ep` (172.30.0.0/24, icc off, no masquerade) + chains `SH_EP_IN`/`SH_EP_FWD`/`SH_EP_DROP`. `net-check.sh`: proxy `401` without a token; host loopback `:8080`, `1.1.1.1`, any DNS name, gateway `:22` all unreachable. Docker 27 rejects `--dns none` ("IP address is not correctly formatted") → the resolver is pointed at the gateway, where 53/udp+tcp is REJECTed (fail fast, not counted). `dmesg_restrict=1` here, so kernel `LOG` lines are unreadable → the per-episode signal is a **count-only iptables rule per container IP** read back at teardown (`dropped_packets` in `net.json`/`finish.json`). Real sealed episode `ep-net-2`: 5 proxy calls, 69,670 prompt + 1,991 completion tokens observed **at the proxy**, `dropped_packets: 0` → `verified_success: true`. Egress fixture (a SOUL telling the agent to `curl` an external IP): 3 packets counted against the container IP on `tcp:80` → `network_egress_attempt` → DQ. **Two false-positive DQs found and fixed while running it**: (1) the rules regexed the whole tool-call argument blob, so a solution whose *script text* contained `"path": "/…"` or mentioned `/ep/out` was disqualified — they now read only the destination/command arguments of a call, never its payload; (2) an absolute write the box **refused** (`write_file` to `/…/report.sh` → "Read-only file system") counted as `wrote_outside_workspace` — the rule now requires the tool to report that the write happened, and treats `/tmp` and `HERMES_HOME` (per-episode tmpfs) as scratch. Both locked in by `tests/test_sh_grade_rules.py`. **One fixture per DQ rule (B5 exit)**: `network_egress_attempt` — real episode `ep-egress`; `protected_path_modified` — a real snapshot with one byte appended to `data/events.log`, re-graded through the grading container → `["protected_path_modified"]`, `verified_success: false` (a SOUL *instructing* the agent to `sed -i` the protected file did **not** work: the agent ignored it, so the deterministic snapshot is the fixture); the four static rules (`read_grader_or_withheld_path_attempt`, `wrote_outside_workspace`, `inline_shell_marker`, `instance_literal_in_bundle`) by unit fixture. |
| V5 | **pass (c=1); c=4 re-running after a proxy fix** | 8 instances of family #1 (difficulty 2) × {NULL, CANON, skill, bashy} = **32 episodes, concurrency 1, 1,879 s of GPU**. Per surface (n=8, verified / overfit / DQ / partial, wall p50 / p90 s, api p50): NULL 8/0/0/0, 30.1/133.5, 5.0 · CANON 8/0/0/0, 41.6/120.2, 5.5 · skill 7/0/0/0, 41.5/50.7, 7.0 · bashy 8/0/0/0, 41.2/115.7, 6.0. **Finding — family #1 at difficulty 2 has no headroom**: NULL `p = 1.0` (8/8), CANON `p = 1.0`, `delta_c = 0.0`, `delta_e` **negative** (CANON spends *more* calls: api p25 6 vs NULL 5) — prose cannot improve on a baseline that already solves it in 5 calls against an `efficiency_reference` of 6. `FamilyStats` still labels it `frontier`, not `trivial`, and correctly so: at 8/8 the Wilson lower bound is 0.676, below the 0.80 band, so one round's evidence is too thin to retire a family. A second round of NULL (16/16 → `wilson_low = 0.805`) is what tips the label, and the p25 rule then retires it. Family #1 needs a harder difficulty before it can carry a round. **Concurrency 4 first attempt exposed a proxy bug, not a GPU limit**: 18 of 32 episodes died on their *first* API call with `401 no valid episode token` (`api_calls: 1`, `failed: true`). The token store was one JSON blob rewritten on every issue — a read-modify-write race, so four episodes starting together read the same blob and the last writer dropped the other three. It is now a directory with one file per token (atomic `write`+`replace` to a digest-named file, `unlink` to revoke), covered by a 64-way concurrent issue test. Per-episode cost was otherwise flat under load (agent wall mean 55.9 s at c=1 vs 76.3 s at c=4 including the failures), so the GPU is not the constraint at this family's size. **Finding — nothing could be made to overfit this family.** Two adversarial surfaces were built to split the halves (published = `bash` route, withheld = `sh` route): `bashy` (a SOUL pushing bash dialect) → 8/8 both halves; then `overfit` — a SKILL.md containing the family's own `CHEAT_BASHISM` script (`declare -A`, `[[ ]]`, `((count[$s]++))`) with a SOUL ordering the agent to copy it **verbatim, byte for byte** → the agent **ignored it and wrote its own POSIX one-liner** (`awk '$2 == "ERROR" { c[$3]++ } END { for (s in c) print s, c[s] }' data/events.log | sort`) → published and withheld both pass. Across **40 episodes** `withheld_pass == published_pass` every time. The family's premise — *"the pinned model writes bash-isms into scripts that dash rejects"* — **does not reproduce at the pin**, so family #1 discriminates nothing regardless of data size. `difficulty` compounds this: it only scales the number of distinct services (`2 + 2·d`), leaving the script to be written identical, so no setting of it creates headroom. |
| V6 | **pass** | `partial` = 0 and `timed_out` = 0 across all 32 V5 episodes plus the 4 boundary fixtures → `partial_rate = 0.0` against the `< 0.10` bar. |
| V7 | pending | |
| V8 | pending | |


## Probe run 1 — where does the baseline actually fail? (2026-09-15)

Eight candidate task *shapes*, 2 NULL runs each, 16 episodes, ≈ 15 min GPU at concurrency 3. `supply/probes/`.

| shape | solved | calls | aimed at |
|---|---|---|---|
| `long_bookkeeping` | **1/2** | 4, 3 | applies one rule to every record instead of the rule each record calls for |
| `git_state` | 1/2 *(the failure was my predicate, not the model — see below)* | 4, 5 | repository state as the deliverable |
| `byte_exact` | 2/2 | 3, 3 | column width, rounding, trailing newline |
| `json_contract` | 2/2 | 3, 3 | right numbers, wrong shape |
| `multifile_edit` | 2/2 | 6, 3 | losing track across six files |
| `perms_and_order` | 2/2 | 3, 3 | modes and ordering treated as incidental |
| `recover_from_error` | 2/2 | 4, 4 | a provided script that refuses to run until its precondition is met |
| `spec_buried` | 2/2 | 4, 4 | acting on the first plausible rule instead of the authoritative one in Appendix C |

**Read (corrected after the sweep below).** The pinned model solved **all eight shapes**: exact byte formatting,
nested JSON contracts, six mechanical edits, modes and ordering, reading a 120-line handbook to the authoritative
appendix, diagnosing a script that fails with a clear message, and per-record bookkeeping — all first time in 3–5
calls. Both apparent failures were authoring bugs of mine, not model failures.

**The `long_bookkeeping` "frontier signal" was an ambiguous prompt.** A size sweep (15 / 30 / 60 / 120 records ×
4 runs) was started to find where the pass rate sat; the first failures showed the cause. The prompt said *"Write
`fees.csv` with `id,fee` for every invoice"*, which reads as an instruction to write a header — so the agent
wrote `id,fee` as line 1 and `line_count_is` failed by exactly one, at **every** size including 15. Every fee
value was correct in every case. The sweep was stopped once the cause was clear; the prompt now says "**no header
line**". Two probe runs, two authoring bugs caught — which is what the stage is for, but it also means a probe
result is only evidence after the failing artefact has been looked at.

**The `git_state` failure was mine.** The predicate demanded `git log | wc -l == 5` because the reference made
two commits; the baseline did the same work in one and scored as a failure. Fixed by asking what the requirement
asks (`git show HEAD:a.txt`) and by adding a third probe guard: an **alternate solution must pass the same
predicates**, or they encode the reference's incidental choices. `supply/probe.py::check`,
`tests/test_probe.py::test_predicates_that_only_accept_the_reference_are_refused`.


## Probe round 2 — the first real frontier shape (2026-09-15)

Four shapes aimed past one-shot single-artefact work, plus the corrected `bookkeeping_120` as a control. 3 NULL
runs each. `supply/probes/harder.py`.

| shape | solved | calls | wall s |
|---|---|---|---|
| **`server_lifecycle`** | **2/3** | **10, 6, 12** | **252, 267, ~270** |
| `cascading_tests` | 3/3 | 5, 4, 4 | ~50 |
| `dirty_csv` | 3/3 | 3, 3, 3 | ~40 |
| `constraint_assign` | 3/3 | 3, 3, 3 | ~40 |
| `bookkeeping_120` *(control)* | 3/3 | 4, 4, 3 | ~60 |

**The control settles the round-1 correction.** With "no header line" in the prompt, 120 records under four rules
is 3/3. The header was the whole signal.

**Three of the four harder shapes are also solved.** Iterate-until-green across three cascading bugs: 4–5 calls.
A CSV with a quoted delimiter, a blank number and a superseding duplicate — the traps `awk -F,` walks into: 3
calls, first time, every time. A constrained assignment a greedy pass does not land: 3 calls.

**`server_lifecycle` breaks it, and breaks it the right way.** 2/3, and the two sibling runs passed the same
instance, so the task is possible and the probe is sound — this is the model, not the fixture. The failure is specific:
`in server.log, dumped does not come before stopped` — the agent stopped the server without ever dumping its
state. The trajectory shows why: it ran `python3 bin/server.py` in the **foreground** (blocking the terminal tool
until it timed out), re-ran it with `background: true`, and then **guessed PID 128** instead of capturing it, so
`SIGUSR1` went to the wrong process. It also costs **10, 6 and 12 calls at ~260 s against the 3–5 calls / 40 s** every solved
shape needs — the cheapest run of this shape is still more expensive than the dearest run of any other — correctness headroom and efficiency headroom in one family.

It is a good family candidate for a further reason: the fix is *sayable*. "Start long-running processes in the
background, capture the pid the tool returns, never guess it, and wait on a readiness file rather than sleeping"
is one paragraph of prose — exactly what the CANON arm has to be able to demonstrate for a family to be admitted
(spec §3.8).


## `server_lifecycle` at 16 runs, and family #2 (2026-09-15)

**Confirming the rate.** 16 NULL runs of the shape at difficulty 1: **14 solved**. Both failures are the same
real one — `state.json does not exist`, the server stopped without ever being asked for its state (one of them
also hit the 600 s timeout). Wilson **[0.64, 0.97]**, so the label is `frontier`, though not far from the trivial
edge. Cost is the louder signal: **5–15 calls** (median 7) against a reference cost of 5, and **67–369 s** wall.
Under the admission rule a gated efficiency metric can admit a family on its own, and this is where the room is.

**A sixth harness bug, found because this family starts processes for a living.** Derivation ran family scripts
with `capture_output=True`. A script that leaves a **background process alive** leaves the pipe open, so
`subprocess.run` blocks on it long after the shell exited — one instance sat for the full 600 s holding a
`compactor.py` nobody was waiting for. Scripts now write to a file and run in their own process group, which is
killed afterwards. (`supply/derive.py::_run_script`.)

**A fifth one, found by the timed-out run.** `before.json` is written by the runner *after* the agent is gone,
so a killed episode has none — and the grader compared protected-path digests against `{}`, marking every path
modified. Every timed-out episode was being disqualified for tampering it never did. A missing baseline is now
unknown rather than "everything changed" (`tests/test_sh_grade_rules.py`).

**Family #2 — `process_lifecycle`.** Derives and gates cleanly on every seed tried (3, 11, 42, 77): 2 published,
6 withheld, each cheat breaking 4 facts. The split is what a shortcut can and cannot fake — a run that never
dumps keeps the file-shape predicates and loses the orderings; a run that forges the artefacts with `printf`
keeps both and loses the `custom` check, which compares the pid the server logged at startup against the pid it
recorded in its own dump. Difficulty is the warm-up (1.5 / 4 / 8 s), which punishes a blind `sleep` without
changing what has to be written. `posix_report` is marked `retired` in the registry.

The pipeline caught one of my own predicates: `ticks > 0` at the moment of the dump was flagged
**non-deterministic** — correctly, since a dump landing within 50 ms of readiness records zero even for the
reference. Removed; the log ordering already asserts what it was reaching for.


**A seventh, from the first screen run.** The `checks.py` loader was written, unit-tested and deployed to the
host — and every grading container still ran the old code, because **the runner ships inside the image**
(`COPY runner/ /runner/`), not in the deployed package. Six episodes died on `grader exited 1` before the cause
was obvious. `hermes-base:pin` is now `sha256:cb21736d…` and `docs/pins.md` records that a runner change means a
rebuild and a new digest.


## First full-pipeline screen — family #2 at difficulty 3 (2026-09-16)

mint → derive → gate → seal → NULL and CANON episodes → `FamilyStats`, end to end, on 6 sealed instances.
**Minting yield 1.0** (6/6 sealed, no rejections); ~1.8 min CPU per instance at an 8 s warm-up, since derive and
gate run the server ~19 times per instance.

| arm | n | verified | wall p50 / p90 s | calls p50 | prompt tokens |
|---|---|---|---|---|---|
| NULL | 6 | **4** | 239 / 298 | 7 | 47.6 k |
| CANON | 6 | **5** | 181 / 488 | 10 | 82.7 k |

`delta_c = +0.333`. NULL Wilson **[0.30, 0.90]**, CANON **[0.57, 1.00]** — the right direction, but at n=6 per arm
the intervals overlap heavily, so **the family is not admitted on this evidence**. The spec's screen is 12 × 8
per arm for exactly this reason; this run is ~1/16 of it and was about proving the pipeline, which it did.

**Difficulty 3 is the right setting.** NULL 4/6 here against 14/16 at difficulty 1 — the 8 s warm-up punishes a
blind `sleep` without changing what has to be written, which is what the difficulty knob is supposed to do.

**A finding that matters for scoring: `delta_e` is _negative_, and it is real.** CANON spends **10 api_calls
against NULL's 7** and passes more often. The obvious suspicion was selection bias — each arm only contributes
the instances it solved, so the weaker arm's successes are its easy ones, and CANON had rescued a hard instance
NULL never solved. `delta_e` was therefore rewritten as a **paired per-instance comparison** over the instances
*both* arms verified, with repeats of one instance averaged before pairing (`sh/validator/stats.py::delta_e`,
`delta_e_paired_instances` in the record; admission now needs ≥ 3 shared instances).

The paired number **disproved the hypothesis**: on the 3 shared instances CANON is *more* expensive, not less —
`api_calls −0.68`, `tool_calls −1.41`, against −0.43 / −1.00 unpaired. So the prose genuinely costs calls on the
same work. The SOUL's last rule — *read the log the program wrote and confirm the steps appear in the order you
meant* — is what buys the correctness, and it is real work. On this family the strategy that makes miners more
correct makes their efficiency term worse. Efficiency is already gated on correctness (§7 counts it only on
verified successes), but a miner following good advice still loses that axis to one who guesses fast and is
lucky. **Open decision** — the paired measure is the right instrument either way; what the scorer does with a
correctness-bought cost increase is not yet settled.

**Capacity: concurrency 4 is too much for this workload.** The first attempt at this screen returned
`server overloaded: no capacity for this request right now` from the engine on all three of Hermes' retries, and
every episode was scored as an unsolved task. Concurrency 2 ran clean. Two consequences: `B` and `T` (spec §5.8)
must be derived at the concurrency the engine actually sustains for the *hardest* family, not the cheapest; and
**a provider outage is now `void`** — not a success, not a failure, not evidence — with `inference_unavailable`
in the signals, excluded from `FamilyStats`, and deliberately left uncached so a resume re-runs it.

**An eighth bug, the third of its kind.** The timed-out CANON episode was disqualified for
`protected_path_modified` even after the runner-side fix, because the **host** substituted an empty
`before.json` into the grading volume when the real one was absent — so the grader never saw "absent", it saw
`{}` and read it as "nothing was there". Re-graded, the episode reports `["timed_out"]` alone.


## First end-to-end round — every stage, one pass (2026-09-16)

`r1`: 3 sealed instances of family #2 at difficulty 3 × {NULL, CANON, two test miners} = 12 episodes, then
close → score → reveal → export → leaderboard. **Every stage ran.** Commitments: 3/3 re-verified at close.
Exports: 6 SFT rows, 1 DPO pair, leak scan clean. Leaderboard rendered from `close.json` alone.

| surface | verified | notes |
|---|---|---|
| NULL | **2/3** | 58 s, 60 s; one genuine failure at 250 s |
| CANON | **0/3** | **all three killed on the 600 s timeout** |
| `5FGoodOperator` (careful, detailed SOUL) | **1/3** | one at 329 s / 14 calls; two timed out |
| `5FHastyRunner` (deliberately careless, terse SOUL) | **3/3** | 61 s, 65 s, 53 s, 5–6 calls |

**The finding that matters: the episode budget, not the strategy, decided this round.** Every timed-out episode
shows the same thing in its container log — `finish_reason='length'`, then Hermes' *"Requesting continuation
(1/4)"*. At the pin's ~45 tok/s decode, one 8192-token response takes ~3 minutes, so five calls exhaust a 600 s
episode. Truncation appears **only** in the verbose-SOUL surfaces (CANON, `5FGoodOperator`); the bare NULL
episodes that passed have none. A detailed strategy makes the model write long plans, long plans hit
`max_tokens`, and the continuation loop eats the clock.

So on this round the **deliberately careless miner beat the careful one 3/3 against 1/3**, and CANON — the
family's own published strategy, the yardstick a family is admitted on — scored `delta_c = −0.67` against its own
baseline. None of that is a fact about the strategies. Three consequences:

  * `timeout_s = 600` and `max_tokens = 8192` are not independent knobs. Either the timeout rises (≈ 1200 s at
    difficulty 3) or `max_tokens` falls; the current pair makes verbosity fatal.
  * A miner can be beaten by an outage of patience rather than of skill, which is the same class of unfairness as
    the harness bugs fixed earlier — and it is **not** currently marked. A timed-out episode counts as a failure.
    Whether a timeout should be a failure or a void is now an open question, and it is not obvious: unlike a
    provider outage, running out of budget *is* partly the strategy's doing.
  * Family #2's difficulty-3 screen numbers are contaminated by this and should be re-run once the budget is
    fixed.

**A ninth bug, in the exports.** The first build reported `dpo_pairs: 0` on a round that plainly had winners and
losers on the same instance. DPO took only the *first* loser per instance, and when that loser was a timed-out
episode it had no trajectory at all, so the pair was dropped silently — by directory order. It now takes the
first side of each pair that actually yields a row. The rebuilt export has the pair it should always have had:
`5FGoodOperator` over `null` on `process-lifecycle-s1-01`.

**Scoring refused to pay anyone, correctly.** Three window episodes is below the 8-episode minimum, so both
miners scored 0 with the reason recorded and shown on the leaderboard. The guard works; a real weight comparison
needs a window, which is what the window is for.


## The cause was sampling, not budget (2026-09-16)

The r1 round's perverse result — careless miner 3/3, careful miner 1/3, CANON 0/3 — is a **sampling artefact**.

Completion tokens per episode, from the proxy's own record (not the agent's self-report):

| surface | completions per call | total | outcome |
|---|---|---|---|
| NULL (passed, 58 s) | 91, 378, 138, 185, 253 | **1,045** | fine |
| CANON s1-00 | 236, 1881, 678, 714, **8192** | 11,701 | timed out |
| CANON s1-01 | 235, **8192**, 2818, 88, 44, **8192**, **8192** | **27,761** | timed out |

27,761 tokens at the pin's ~45 tok/s is 617 s — the 600 s timeout, exactly. And the capped responses chain:
8192 → continuation → 8192 → continuation → 8192, for a task whose whole content is *start a server, signal it,
stop it*. That is degenerate repetition, not planning.

**The test.** Same instance, same CANON bundle, one variable changed — the proxy's pinned `temperature`,
0.2 → 0.7:

| | temperature 0.2 | temperature 0.7 |
|---|---|---|
| completion tokens | 27,761 | **4,672** |
| truncations | 3 | **0** |
| wall | timed out (> 600 s) | **273 s** |
| graded | — | **`verified_success: true`** |

A 6× reduction in decode, the continuation loop gone, and the episode passes the withheld half. Low temperature
was putting the model into repetition loops, and the loops — not the strategy, not the difficulty, not the
timeout — decided the round.

**Consequences.** Every number measured at `temperature 0.2` is contaminated: family #2's difficulty-3 screen
(NULL 4/6, CANON 5/6), the whole r1 round, and the `delta_e` finding that CANON "costs more calls" — that last
one is now the most likely casualty, since verbose repetition inflates exactly the metric it was measured on.
The 16-run `server_lifecycle` sweep at difficulty 1 is less affected (short episodes, few truncations) but
should be re-checked.


## The A/B, on the whole round (2026-09-16)

Identical instances, bundles, image, boundary and grader; one variable — the proxy's pinned `temperature`.

| surface | 0.2 | 0.7 |
|---|---|---|
| CANON | **0/3**, 3 timeouts | **3/3**, 0 timeouts |
| `5FGoodOperator` (careful) | 1/3, 2 timeouts | **2/3**, 1 timeout |
| `5FHastyRunner` (careless) | 3/3 | 3/3 |
| NULL | 2/3 | 1/3 |
| **timeouts, all surfaces** | **5 / 12** | **2 / 12** |

The perverse ordering is gone. At 0.2 the family's own published strategy scored `delta_c = −0.67` against its
own baseline; at 0.7 it scores **+0.67** — CANON 3/3 against NULL 1/3. That is the family behaving the way a
prose discriminator is supposed to, and it was invisible under the sampling bug.

`delta_e` is now −0.125 / −0.25 on **one** paired instance, which is below the 3-instance floor the screen
requires and is not evidence of anything. The earlier "prose costs calls" finding rests on numbers measured at
0.2 and should be treated as withdrawn until the screen is re-run.

NULL moving 2/3 → 1/3 is n = 3 noise, not a finding. Neither round can score a miner: three window episodes is
below the 8-episode minimum, and both closes correctly paid zero with the reason recorded.
