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
