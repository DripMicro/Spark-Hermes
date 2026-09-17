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
| agent image | `hermes-ubuntu:pin` — ubuntu:22.04 + uv (PyPI) + uv-managed CPython 3.12 in `/opt/uvpython` + hermes-agent at the commit above + pytest 8.3.5 on the system interpreter + the runner. The venv is *last* on PATH so a task's own `python3` wins in the shell; the runner is started by absolute path. Built on the worker (91.224.44.85): `sha256:128f11bce99f…` | `sh/validator/images/build.sh` |
| episode network | `sh-ep` 172.30.0.0/24, gateway 172.30.0.1, proxy on `:8090`; `--dns 172.30.0.1` with 53 REJECTed (Docker 27 has no `--dns none`); a counted DROP rule per container → `network_egress_attempt` | `sh/validator/net/` |
| sandbox | uid 1000, no capabilities, no new privileges, pids 512, 4 GB, tmpfs home (the grader: pids 256, 2 GB); the grader takes the protected paths' baseline from the task image itself, never from the runner (which shares the agent's uid), and the runner's output directory is recreated before anything is written to it; the workspace is the image's own tree for image-defined tasks (writable), `/ep/ws` otherwise (read-only rootfs); the grader is a fresh read-only container with a tmpfs at the workdir | `sh/validator/episode.py`, `sh/validator/grade.py` |
| scoring | `sh-scoring-v3` (from r0004): an episode counts by its **credit** — the share of the task's withheld checks that hold (0–1; 0 when disqualified) — not all-or-nothing. On r0003 nobody passed every check while agents passed 19–41 % of them. Overfit = published share − withheld share ≥ 0.5 (tasks with a published half only). Paired Δ of credit vs the NULL arm on the same instances, se with the reference term, Δc = max(0, mean − 1.28·se); efficiency gated; window pooled over the last 8 rounds for references and miners alike; min 8 window episodes; overfit / DQ / near-duplicate zeroing | `sh/scoring/v2.py` |
| commitment | `salt = HMAC(secret, "sh-salt\|task_id)`, `commitment = "hmac-sha256:" + HMAC(salt, canonical_json(withheld))`; revealed at close | private `supply/seal.py`, `sh/validator/round.py` |

## Round clock (2026-09-16)

| Parameter | Pin | Where |
|---|---|---|
| submission window | **120 min** from open; the seal is taken at close, by PR head SHA. A window that closes with no valid submission (an incumbent alone does not count) **reopens**: same round, same tasks, a fresh 120 min, recorded in `window.json` (`reopened`, `reason`) — nothing is sealed, evaluated or revealed. `submissions/` carries exactly the current king: a dethroned incumbent is removed at announce | `sh/validator/orchestrate.py --window-minutes` |
| tasks per round | up to 8 (a round opens with what the daemon sealed; r0004 opened with 5), minted ahead by `supply.queue` (`--ahead 3`); future rounds published only as digests in `rounds/queue.json`, over the tasks and their previews. For a previewing family (`swe_fix`) miners get the previews at open and the evaluated tasks at close | private repo |
| attestation | `sh-attestation-v2`: `sr25519(hotkey, "spark-hermes:<repo>:<round>:<bundle_sha256>:<signed_at>")` in `attestation.json`. One submission per hotkey per round: the **latest signed** counts (not the newest PR — signed bundles are public and could be reopened by anyone); a signing time more than 10 min in the future is refused. From r0004 | `sh/cli/attest.py`, `orchestrate.one_per_hotkey` |
| S1 — copied answers | a challenger sharing more than 8 distinct solution lines (≥ 24 chars) or more than 40 distinct 12-token runs with the round's private reference/alternate solutions and verifiers (for `swe_fix`: the code its bugs replaced) — text that also appears in a task's prompt, or in a preview's, excluded — is refused at seal. Calibrated on r0003: every mock bundle, the canon and the incumbent share 0; a pasted reference shares 186 lines, a 12-line snippet 12 lines, a verifier reflowed into prose 504 runs. From r0004 | `sh/validator/similarity.py` |
| crown | best Δ credit vs baseline on **this round's** instances, > 0, ≥ 4 paired; ties by pooled Δc | `sh/scoring/crown.py` |
| payment | pooled over the last 8 rounds from r0004 (rounds scored all-or-nothing are not pooled); Δc = one-sided 90 % lower bound of Δ credit | `sh/scoring/v2.py`, `--window-from` |
| training data | SFT: the king's episodes where **every** check holds; DPO: the king's episode with credit ≥ 0.8 vs another surface's with at least 0.5 less, same instance; no king → nothing uploaded | `sh/exports/build.py` |

## Family #4 — `swe_fix` (2026-09-17)

| Component | Pin | Where |
|---|---|---|
| seed material | SWE-smith (`SWE-bench/SWE-smith`, MIT): bugs injected into real Python repositories, each with an issue-style problem statement, the bug's diff, the tests it breaks (FAIL_TO_PASS) and the tests it leaves passing (PASS_TO_PASS), on a per-repository environment image. Indexed: 23,129 usable of 59,136 (a problem statement, 1–10 broken tests, ≥ 5 passing, a diff that touches no test infrastructure). Rounds draw from 12 pure-Python repositories. Each bug is used at most once | private `supply/swesmith.py`, `supply/families/swe_fix/repos.json` |
| pilot | 20 bugs over 5 repositories, pinned model with no strategy, alone on the GPU: 17 valid, mean credit **0.34**, 4 fully resolved, 4 partly, 9 not at all; no kept test broken; 9 of 17 used all 30 turns | 2026-09-17 |
| task images | `swe-task:<opaque key>` = the environment image at the bug's branch with its **git history cut to one commit** and no bytecode compiled before the bug (a pilot agent read the injected diff out of `git log`), plus the Hermes layers of `hermes-ubuntu:pin`. Built once, on the worker; `images/<key>/SOURCE.json` names the dataset, license, repository and environment — never the bug | private `supply/swesmith.py` |
| previews | miners are shown **different bugs from the ones scored**: each evaluated bug has a preview — another bug from the same repository and environment, with its SWE-smith instance id so it can be reproduced locally — and only previews are in `rounds/<id>/tasks/` while the window is open. A strategy is paid for debugging these codebases, not for knowing eight one-line answers. The evaluated tasks are published at close in `rounds/<id>/evaluated/`, and `reveal.json` names each one's SWE-smith instance id — the committed test ids are that bug's own tests, readable in the dataset; `rounds/queue.json` commits to both before the round opens | `supply/families/swe_fix/family.py`, `orchestrate.shown` |
| universe | one `custom swe_test <node id>` per broken test, **all withheld** (split `withheld`: nothing published, so no overfit rule applies and a partial fix is partial credit). The grader receives the broken tests' files (as they were before SWE-smith deleted those tests) and the kept tests in `withheld.json.assets`, never the agent | `supply/families/swe_fix/checks.py` |
| grading | in a fresh read-only container over the agent's final tree: bytecode deleted; test infrastructure the task did not ship (a new `conftest.py`, `sitecustomize.py`, `.pth`, `pytest.ini`, anything under `tests/`) removed; the broken tests written back; one `pytest --verbose` run parsed the way SWE-smith parses it. A broken test counts only if it passes **and no kept test fails**. Shipped test infrastructure is a protected path: modifying it disqualifies | `checks.py`, `sh/validator/grade.py` |
| kept tests | up to 60 passing tests from the broken tests' files and 40 from elsewhere, sampled per bug; at mint, only those that pass both on the bug and after the reference are kept | `swesmith.sample_p2p`, `family.kept_tests` |
| derivation | every broken test fails on the untouched tree and passes after the reference (the bug's diff reversed), twice; the gate re-proves it | private `supply/derive.py`, `supply/gate.py` |
| admission | one baseline episode per sealed task; admitted when the pinned model with no strategy does **not fully** fix it (credit < 1). A baseline 0 is admitted: unlike FACET, a real bug with its failing tests is fixable, and 0 is where strategies have the most room | `ops/start-queue.sh --screen-band 0.0:0.99` |
| S1 | compared with the code the bug replaced (the diff's removed lines), not with the diff's context or the repository's tests, which quote the repository miners can read | `sh/validator/similarity.py` |
| limits | `max_turns` 30, `timeout_s` 600, tools `terminal` + `file`, network none; suite timeout 480 s (inside the executor's and the grader's budgets) | `family.py` |

## Retired

- `terminal_task` (family #3, FACET-Terminal-6k, rounds r0003–): real terminal tasks with pytest verifiers, transformed at mint, cheats = partial deliverables. Retired 2026-09-17: the pinned model earned ~0 credit on most tasks (r0003: 6 of 8 at 0 % for every surface) and screening at 10–70 % admitted none of its first screens. Its code stays in the private repo so rounds already minted can be evaluated.
- `posix_report` (family #1, 2026-09-14): the pinned model solved it without a strategy; no headroom.
- `process_lifecycle` (family #2, rounds s1–r0002): authored template; the baseline passed 7/8, one instance of headroom. Removed with its code on 2026-09-16 (`family-process-lifecycle:pin` = `sha256:cb21736d…`, `hermes-base:pin` = the python:3.12-slim agent image these ran on).
- `temperature 0.2` (era A0): repetition loops; see sampling above.
