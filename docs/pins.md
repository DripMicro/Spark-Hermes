# Pins (Week 0, item 0.3) — draft for announce.json

| Component | Pin | Source |
|---|---|---|
| hermes-agent | commit `d84ece48b8552501660be229797e2d2aa4cee8db` (main, 2026-09-15T16:29Z), v0.21.3, requires-python >=3.11,<3.14 | gh api |
| model | `gittensor-model-hub/Qwen3.8-27B-NVFP4-RTX5090` — revision: TBD (resolve the commit sha, never `main`) | HF (public) |
| inference engine | `ghcr.io/gittensor-ai-lab/sparkinfer-qwen38:0.5.7` = `sha256:c919d647e8ae873837ad2cbcb83935cb9949765f1480637f9495c1ae7643d85b` | ghcr |
| CTX | **65536** | Hermes requires ≥ 64K advertised (V2); KV ≈ 11.5 KB/token so 64K costs < 1 GB at low concurrency; 262144 OOMed at concurrency 4 |
| sampling | **`temperature 0.7`**, `top_p 0.95`, `max_tokens 8192`, proxy-enforced (a bundle cannot change them). **Not a preference — 0.2 drives the model into repetition loops that burn 6× the decode and kill episodes on the timeout** (`docs/spikes.md`, 2026-09-16). Confirmed by a whole-round A/B (2026-09-16): timeouts 5/12 → 2/12, CANON 0/3 → 3/3, `delta_c` −0.67 → +0.67. | `sh/validator/proxy.py` |
| hermes-base image | `hermes-base:pin` = `sha256:cb21736dab40caa05d6fcf16d9d79b579472bfd61c257be48c28ac0ec8ce946a` (was `49224eca…` at A0; system Python 3.12, uv downloads disabled). **The runner ships inside this image** (`COPY runner/ /runner/`), so any change to `run_episode.py` or `grade.py` needs a rebuild and a new digest here — the `checks.py` loader was written, tested and deployed to the host while every container still ran the old runner, and the screen failed on it. | |
| family images | `family-process-lifecycle:pin` = `sha256:cb21736dab40caa05d6fcf16d9d79b579472bfd61c257be48c28ac0ec8ce946a` (rebuilt with hermes-base) (family #2; tools only, `FROM hermes-base:pin`). `family-posix-report:pin` retired with its family. | |
| episode network | `sh-ep` 172.30.0.0/24, gateway 172.30.0.1, proxy on `:8090`; `--dns 172.30.0.1` with 53 REJECTed (Docker 27 has no `--dns none`) | `sh/validator/net/net-up.sh` |

Host: `root@91.224.44.223:50199` — RTX 5090 32 GB, Docker 27.3.1, nvidia runtime OK. Jupyter on `0.0.0.0:8888` — owner to close/bind (Week 0, 0.2).

2026-09-16 — `sh/validator/runner/grade.py` gained an import fallback (`sh.predicates` when `/runner/predicates` is absent) so the validator's tests can load it outside the image. Inside the image the first import succeeds as before; behaviour is identical and no rebuild is needed. The image build now copies `sh/predicates` into the runner instead of keeping a second copy in the tree.

## Round clock (2026-09-16)

| Parameter | Pin | Where |
|---|---|---|
| submission window | **120 min** from open; the seal is taken at close, by PR head SHA. `submissions/` carries exactly the current king: a dethroned incumbent is removed at announce | `sh/validator/orchestrate.py --window-minutes` |
| tasks per round | 8, minted ahead by `supply.queue` (`--ahead 3`); future rounds published only as digests in `rounds/queue.json` | private repo |
| attestation | `sr25519(hotkey, "spark-hermes:<round>:<bundle_sha256>")` in `attestation.json`; one PR per hotkey per round, newest counts | `sh/cli/attest.py` |
| crown | best Δ vs baseline on **this round's** instances, > 0, ≥ 4 paired; ties by pooled Δc | `sh/scoring/crown.py` |
| payment | pooled over the last 8 rounds; Δc = one-sided 90 % lower bound | `sh/scoring/v2.py` |
| training data | the king's verified episodes only (SFT); king vs any failing surface on the same instance (DPO); no king → nothing uploaded | `sh/exports/build.py` |

## Family #3 — `terminal_task` (2026-09-16)

| Component | Pin | Where |
|---|---|---|
| seed material | FACET-Terminal-Tasks-6k (`hamishivi/agent-task-facet-terminal-6k`, Apache-2.0): 6,020 tasks, each an instruction, a `FROM ubuntu:22.04` environment, a reference `solve.sh`, a pytest verifier | private `data/facet/` |
| hermes-ubuntu image | `hermes-ubuntu:pin` — ubuntu:22.04 + uv 0.9.7 + uv-managed CPython 3.12 (`/opt/uvpython`) + hermes-agent `d84ece48…` + pytest 8.3.5 on the system interpreter + the runner. Worker build `sha256:112537928c4b…`; validator build `sha256:122e6b653478…` (same pin, not bit-identical — derivation runs on the validator's, episodes on the worker's) | `sh/validator/images/hermes-ubuntu/Dockerfile` |
| task images | `facet-task:<env hash[:16]>` = the task's Dockerfile with `FROM hermes-ubuntu:pin`, the workdir handed to uid 1000; built on the validator at mint and on the worker at evaluate from `rounds/<id>/images/<hash>/` | `supply/facet.py`, `orchestrate.evaluate` |
| universe | one `custom facet_test:<test id>` per verifier test case; the test file reaches the grader in `withheld.json.assets`, never the agent | `supply/families/terminal_task/checks.py` |
| cheats | partial deliverables: the reference, then all but the first k of the files it created removed (k = 1, n/2, n−1); a single deliverable cut to half. 94 % of FACET solutions are one Python heredoc, so line truncation could only yield "nothing done", which `derive` rightly refuses as a wrong answer rather than a cheat | `family.cheats_for` |
| limits | `max_turns` 30, `timeout_s` 600, tools `terminal` + `file`, network none, uid 1000 | `family.py` |
| retired | `posix_report` (#1) and `process_lifecycle` (#2) removed with their code on 2026-09-16 | — |
