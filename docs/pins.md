# Pins

What every round is measured against. A change to any row changes what miners are scored on, so it is a
deliberate, dated act — and a new era when it changes the reference arms' comparability.

## Current (era `e0`)

| Component | Pin | Where |
|---|---|---|
| hermes-agent | commit `d84ece48b8552501660be229797e2d2aa4cee8db` (main, 2026-09-15T16:29Z, v0.21.3) | `sh/validator/images/hermes-ubuntu/Dockerfile` |
| model | `gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090` — revision: TBD (resolve the commit sha, never `main`) | HF |
| inference engine | `ghcr.io/gittensor-ai-lab/sparkinfer-qwen38:0.5.7` = `sha256:c919d647e8ae873837ad2cbcb83935cb9949765f1480637f9495c1ae7643d85b` | ghcr |
| context | **65536** — Hermes requires ≥ 64K advertised; 262144 OOMed at concurrency 4 | engine |
| sampling | **`temperature 0.7`**, `top_p 0.95`, `max_tokens 8192`, proxy-enforced (a bundle cannot change them). 0.2 drives the model into repetition loops that burn 6× the decode and kill episodes on the timeout (`docs/spikes.md`; whole-round A/B: timeouts 5/12 → 2/12, canon 0/3 → 3/3) | `sh/validator/proxy.py` |
| agent image | `hermes-ubuntu:pin` — ubuntu:22.04 + uv (PyPI) + uv-managed CPython 3.12 in `/opt/uvpython` + hermes-agent at the commit above + pytest 8.3.5 on the system interpreter + the runner. The venv is *last* on PATH so a task's own `python3` wins in the shell; the runner is started by absolute path. Built on the worker: `sha256:7017979f522f…` | `sh/validator/images/build.sh` |
| episode network | `sh-ep` 172.30.0.0/24, gateway 172.30.0.1, proxy on `:8090`; `--dns 172.30.0.1` with 53 REJECTed (Docker 27 has no `--dns none`); a counted DROP rule per container → `network_egress_attempt` | `sh/validator/net/` |
| sandbox | uid 1000, no capabilities, no new privileges, pids 256, 4 GB, tmpfs home; the workspace is the image's own tree for image-defined tasks (writable), `/ep/ws` otherwise (read-only rootfs); the grader is a fresh read-only container with a tmpfs at the workdir | `sh/validator/episode.py`, `sh/validator/grade.py` |
| scoring | `sh-scoring-v2`: paired Δ vs the NULL arm on the same instances, se with the reference term, Δc = max(0, mean − 1.28·se); efficiency gated; window pooled over the last 8 rounds for references and miners alike; min 8 window episodes; overfit / DQ / near-duplicate zeroing | `sh/scoring/v2.py` |
| commitment | `salt = HMAC(secret, "sh-salt\|task_id)`, `commitment = "hmac-sha256:" + HMAC(salt, canonical_json(withheld))`; revealed at close | private `supply/seal.py`, `sh/validator/round.py` |

## Round clock (2026-09-16)

| Parameter | Pin | Where |
|---|---|---|
| submission window | **120 min** from open; the seal is taken at close, by PR head SHA. A window that closes with no valid submission (an incumbent alone does not count) **reopens**: same round, same tasks, a fresh 120 min, recorded in `window.json` (`reopened`, `reason`) — nothing is sealed, evaluated or revealed. `submissions/` carries exactly the current king: a dethroned incumbent is removed at announce | `sh/validator/orchestrate.py --window-minutes` |
| tasks per round | 8, minted ahead by `supply.queue` (`--ahead 3`); future rounds published only as digests in `rounds/queue.json` | private repo |
| attestation | `sh-attestation-v2`: `sr25519(hotkey, "spark-hermes:<repo>:<round>:<bundle_sha256>:<signed_at>")` in `attestation.json`. One submission per hotkey per round: the **latest signed** counts (not the newest PR — signed bundles are public and could be reopened by anyone); a signing time more than 10 min in the future is refused. From r0004 | `sh/cli/attest.py`, `orchestrate.one_per_hotkey` |
| S1 — copied answers | a challenger sharing more than 8 distinct solution lines (≥ 24 chars) or more than 40 distinct 12-token runs with the round's private reference/alternate solutions and verifiers — text that also appears in a task's prompt excluded — is refused at seal. Calibrated on r0003: every mock bundle, the canon and the incumbent share 0; a pasted reference shares 186 lines, a 12-line snippet 12 lines, a verifier reflowed into prose 504 runs. From r0004 | `sh/validator/similarity.py` |
| crown | best Δ vs baseline on **this round's** instances, > 0, ≥ 4 paired; ties by pooled Δc | `sh/scoring/crown.py` |
| payment | pooled over the last 8 rounds; Δc = one-sided 90 % lower bound | `sh/scoring/v2.py` |
| training data | the king's verified episodes only (SFT); king vs any failing surface on the same instance (DPO); no king → nothing uploaded | `sh/exports/build.py` |

## Family #3 — `terminal_task` (2026-09-16)

| Component | Pin | Where |
|---|---|---|
| seed material | FACET-Terminal-Tasks-6k (`hamishivi/agent-task-facet-terminal-6k`, Apache-2.0): 6,020 tasks, each an instruction, a `FROM ubuntu:22.04` environment, a reference `solve.sh`, a pytest verifier. Each task is used at most once | private `data/facet/` |
| task images | `facet-task:<env hash[:16]>` = the task's Dockerfile with `FROM hermes-ubuntu:pin`, what the reference would install provisioned at build, the workdir handed to uid 1000. Built **once, on the worker**: the queue daemon drives the worker's Docker over ssh (`DOCKER_HOST`), so the image a task was derived in is the image its episodes run in; each image's Dockerfile and `SOURCE.json` are published with the round | `supply/facet.py`, `ops/start-queue.sh` |
| universe | one `custom facet_test:<test id>` per verifier test case; the test file reaches the grader in `withheld.json.assets`, never the agent | `supply/families/terminal_task/checks.py` |
| transform | every instance is transformed at mint, seeded: data/document files the instruction names are renamed (synonyms + a short tag) in the instruction, the reference, the verifier and the task's own files; float values in JSON inputs are scaled ±5–15 % (ids, versions, ports, coordinates and timestamps excluded; skipped when the verifier hard-codes numbers) and rewritten wherever quoted. The image tag and `images/<key>/` are opaque, and `SOURCE.json` names the dataset and license, never the upstream task. Derivation re-proves the transformed task by execution. From r0004 | private `supply/transform.py`, `supply/facet.py` |
| cheats | partial deliverables: the reference, then all but the first k of the files it created removed (k = 1, n/2, n−1); a single deliverable cut to half. Line truncation cannot work — 94 % of FACET solutions are one Python heredoc | `family.cheats_for` |
| limits | `max_turns` 30, `timeout_s` 600, tools `terminal` + `file`, network none | `family.py` |

## Retired

- `posix_report` (family #1, 2026-09-14): the pinned model solved it without a strategy; no headroom.
- `process_lifecycle` (family #2, rounds s1–r0002): authored template; the baseline passed 7/8, one instance of headroom. Removed with its code on 2026-09-16 (`family-process-lifecycle:pin` = `sha256:cb21736d…`, `hermes-base:pin` = the python:3.12-slim agent image these ran on).
- `temperature 0.2` (era A0): repetition loops; see sampling above.
