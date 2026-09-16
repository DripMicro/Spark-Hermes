# Seed material for hybrid task families (2026-09-16)

The families in the private repo generate tasks from code and a seed. A **hybrid family** takes real material as
input — an existing task with an environment, a reference solution and a verifier — and still derives the
published/withheld halves by executing reference, alternates and cheats. This is the survey of what fits the
pinned stack (Hermes agent with `terminal` + `file` tools, network off; Qwen3.8-27B, whose launch benchmarks are
Terminal-Bench 2.1, SWE-bench Pro, NL2Repo-Bench, DeepSWE 1.1, QwenSWEBench).

| Dataset | Size | Shape | Fits because | License | Caveat |
|---|---|---|---|---|---|
| **Terminal-Bench 2.0 / 2.1-verified** (`harborframework/terminal-bench-2.0`, `zai-org/terminal-bench-2-verified`) | 89 | instruction.md · task.toml · Dockerfile · `solution/` · `tests/` (~28 tests/task) | exactly our task shape; Hermes ships a `TerminalBench2EvalEnv` for it; Qwen3.8 is measured on it | Apache-2.0 | eval set — hold out, never train on |
| **Terminal-Bench Pro** (alibaba, 200 public) | 200 | Harbor layout, 8 domains | same shape, 2× the tasks, sysadmin/security/data included | Apache-2.0 | solutions not published for all |
| **FACET-Terminal-6k** (`hamishivi/agent-task-facet-terminal-6k`) | 6,020 | instruction + built image + **reference solution + verifier**, per-task dir, byte-for-byte | the only large set with all four artefacts we need; synthesized from agent skills, repaired by execution — the same philosophy as `derive` | Apache-2.0 | images must be rebuilt (script provided); synthetic quality varies |
| **CLI-Universe-6K** (paper 2606.22883) | 6,000 traj. | trajectories from a verifiable-synthesis engine | shows the recipe scales (Qwen3-32B → 33.4 % TB2) | CC BY-SA 4.0 | trajectories, not tasks; share-alike |
| **SWE-smith** (`SWE-bench/SWE-smith`) | 50,137 | repo · image · `patch` · FAIL_TO_PASS/PASS_TO_PASS · problem statement | executable, MIT, Hermes' own `HermesSweEnv` targets SWE tasks; the patch is the reference, the failing tests are the verifier | MIT | Python-only, repo-scale workspaces (heavy images) |
| **SWE-rebench V2** (`nebius/SWE-rebench-V2`) | 32,079 | real issue/PR pairs, 20 languages, per-task image | continuously refreshed, decontaminated, multi-language | CC BY 4.0 (+ per-repo) | must honour each repo's license at export |
| **R2E-Gym V1** (`R2E-Gym/R2E-Gym-V1`) | 8,101 | commit-derived tasks, image, tests, expected output | procedural SWE-GEN tasks without human issues | Apache-2.0 | 13 repos; large parquet |
| **InterCode-Bash / NL2Bash-EABench** | 1,000 / 150 | NL instruction → bash, file-system grounded, executable check | small, cheap, shell-only; good for a light family | MIT / see repo | thin verifiers (one command) |
| **Harbor-Mix** (`harborframework/harbor-mix`) | 100 | curated meta-set across 34 benchmarks | broad signal, cheap | CC BY 4.0 | 27 tasks LLM-judged — not usable as withheld checks |

## Recommendation

1. **First hybrid family: `terminal_task` over FACET-6k.** Each row already carries instruction, environment,
   reference solution and verifier; the family's job is only (a) to snapshot the container state into a fixture
   (or pin the image), (b) to author the *cheats* generically — delete or stub the verifier's targets, forge the
   output with `printf`, skip the long-running step — and (c) to let `derive` split the verifier's assertions into
   published/withheld by which cheats break them. Tasks whose verifier is a single assertion get no withheld half
   and are dropped by the gate, which is the right filter.
2. **Second: `swe_fix` over SWE-smith** (MIT, Hermes-native). Reference = the patch; verifier = FAIL_TO_PASS;
   cheats = "edit the test", "hard-code the expected value", "revert PASS_TO_PASS" — all derivable from the row.
   Workspaces are repo-scale, so the family image must carry the repo's environment (`image_name`), which means
   one family image per repository rather than one per family; budget for that on the worker.
3. **Hold out Terminal-Bench 2.x and Terminal-Bench Pro** as the public yardstick: never seed rounds from them,
   report the pinned model's score on them per era, and let miners see that the competition transfers.
4. Everything exported to the training dataset keeps the upstream license and attribution per row
   (`source`, `source_id`, `license` fields in the SFT/DPO schema) — SWE-rebench and Harbor-Mix require it.
