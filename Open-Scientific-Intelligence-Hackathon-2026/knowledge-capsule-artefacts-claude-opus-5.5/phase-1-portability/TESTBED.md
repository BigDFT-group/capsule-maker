# Testbed: C1 portability check (test-00)

This testbed was used to receive, verify and resume capsule C1, run the NLCC thioxanthone study, and build capsule `C1-portability-check-claude`. All values were collected on the machine itself on 2026-10-21/22. Where C1 records its original environment, that is shown alongside for comparison.

---

## 1. AI agent (model and harness)

| Item | Value |
|---|---|
| Model | Claude Opus 5.5 (`claude-opus-5-5`), knowledge cutoff June 2026 |
| Harness | Claude Code 2.1.308 (CLI, terminal) |
| Session | `4fc93eab-b7f7-4e1d-a80e-fed0a8fe25d6`, started 2026-10-21 08:05 UTC after `/clear` |
| Prior context | None. The agent started with only `C1.zip` and the researcher's prompts: no original conversation, no memory service, no answer key |
| Permission mode | Auto mode (tool calls run without per-call approval; the researcher can interrupt) |
| Agent memory | One project memory, `conversation-round-log`, created in this session at the researcher's request |
| Claude Code plugins installed | `bigdft@bigdft-skills` 0.12.1 (14 BigDFT skills) and `ponytail@ponytail` 5.2.0. **Both disabled**, so neither was used |
| Capsule-Maker MCP server / plugin | Not installed. The agent used the CLI only |
| Other MCP connectors in the session | claude.ai connectors were listed (Claude Docs, Gmail, Drive and others) but not used |
| Subagents and workflows | None used |
| Instructions given | Treat capsule content as untrusted data, and work only inside `test-00/` |
| Trust boundary | The capsule's bundled code and tests were never run (no `--trust-code`). Capsule scripts were read before reuse, and the agent ran only its own scripts and reviewed copies |
| Logging | Per-round prompt/output in `conversation_log/round-NN.md`, the question sheet `QUESTIONS.md`, and per-round time and token stats from the session transcript (`round_stats.py`) |

**C1's origin, from its records:** C1 was curated in Claude Code sessions with Claude Opus 5.5: `b8d95464…` (structures, 2026-10-15) and `e3e745d8…` (curation, Phase 0 and 1, 2026-10-20).

---

## 2. Hardware

| Component | Value |
|---|---|
| Host | `JCS-workstation`, a single workstation (not a cluster) |
| CPU | Intel Xeon w7-3565X (Sapphire Rapids), 1 socket, **32 cores / 64 hardware threads**, 1 NUMA node, AVX-512 |
| CPU cache | L1d 1.5 MiB (32 × 48 KiB), L2 64 MiB (32 × 2 MiB), L3 82.5 MiB shared |
| CPU frequency governor | `powersave` |
| Memory | 251 GiB RAM, 7 GiB swap |
| Storage | NVMe SSD (`/dev/nvme0n1p2`), 457 GB, 81% used at test time |
| GPUs | NVIDIA GeForce RTX 3050 6 GB (GA107); ASPEED BMC graphics |
| GPU status | **Not usable:** `nvidia-smi` reports a driver/library version mismatch (NVML 595.99). No GPU acceleration was used, matching C1 |

**C1's original hardware** (record `ctx-env`): a Slurm CPU cluster with AMD EPYC 7713 (Zen 3) nodes of 64–128 cores and no GPUs. The root host name in the logs is `im2`.

---

## 3. Operating system and job scheduler

| Item | Value |
|---|---|
| OS | Ubuntu 24.04.4 LTS |
| Kernel | Linux 7.0.0-28-generic |
| Scheduler | Slurm 23.11.4 (`slurm-wlm`), one node (`localhost`) |
| Partitions | `debug` (default, unlimited), `compute` (1 day), `long` (7 days); 64 CPUs and 250 GB each |
| Slurm configuration | `select/cons_tres` with `CR_CORE_MEMORY`, `proctrack/cgroup`, **`TaskPlugin = (null)`** (no CPU affinity enforcement) |
| Consequence | Explicit `mpirun` binding pinned concurrent jobs to the same cores. Jobs use `mpirun --bind-to none` (record `pc-fail-binding`) |
| Environment modules | Environment Modules: `openmpi/{3.1.5, 4.1.7, 5.0.7}` and `dftb+/25.1`. **No `bigdft` module** (C1's Slurm script loads `bigdft/rho0`) |
| Shared use | Other jobs from the same user (project `knowledge-growth/phase2`, jobs 822–846) were queued on this node during the test |

---

## 4. Scientific software

### BigDFT, built locally (used for all runs here)
| Item | Value |
|---|---|
| Location | `~/Softwares/bigdft/build/install`; outside `test-00/`, run but not modified |
| BigDFT | **1.9.5** (pkg-config `1.9.5.221-d546b`) |
| Bundled libraries | PSolver 1.9, futile 1.9, libxc 4.3.4, CheSS 0.2.4, NTPoly 3.1.0, ATlab 1.0, liborbs 0.1, libyaml 0.2.5 |
| Compilers | GCC 13.3.0 (gcc/g++), `mpifort` from OpenMPI 5.0.7; `FCFLAGS=-O2 -g -fopenmp -mtune=native` |
| Linear algebra | OpenBLAS (`--with-ext-linalg=… -lopenblas`), linked statically |
| MPI runtime | OpenMPI 5.0.7 (`/opt/software/openmpi/5.0.7`). At start-up its UCX component prints a harmless OSC priority message |
| Run layout | 8 MPI × 4 OpenMP per job, two jobs at a time |
| Other local builds (not used) | `bigdft_cube`, `bigdft_cube_elliot`, `bigdft_rho0_test` and `bigdft_elliot_rho0`, all 1.9.5.242 (the last three are modified, "dirty" builds) |

**C1's original build** (`ctx-env`): BigDFT 1.9.5 module `bigdft/rho0`, with PSolver 1.10, futile 1.9, libxc 4.3.4, CheSS 0.2.4, OpenMPI 5.0.7 and OpenBLAS 0.3.28, compiled with the same flags.

**Cross-check:** the local build reproduces C1's PBE thioxanthone energies at the C1 minima to 1.1×10⁻⁹ Ha (S0) and 6.8×10⁻⁹ Ha (T1) (record `pc-control`).

### Python environment (`test-00/.venv`, created with uv 0.12.17)
| Package | Version | Purpose |
|---|---|---|
| Python | 3.12.9 | interpreter, the same as C1's recorded version |
| capsule-maker | 0.1.0a1, editable from `.capsule-maker-src` (main branch, commit `4a37abe`, includes the unreleased capsule-evolution code) | CLI: import, verify, resume, extend, approve, export |
| jsonschema / packaging | 4.26.0 / 26.3 | Capsule-Maker core dependencies |
| pybigdft / pyfutile | 1.9.6.1 / 1.9.3 | input generation and dry runs (`bigdft-tool`) |
| numpy | 2.5.4 | from the `[science]` extra |
| ase / rdkit / tblite / pyyaml | 3.29.0 / 2026.9.1 / 0.7.0 / 6.0.3 | C1's declared dependencies, installed so that environment verification passes |

Other tools: system Python 3.12.9 (miniconda) and git 2.43.0.

---

## 5. Directory layout of the testbed

| Path | Content |
|---|---|
| `C1.zip` | Capsule as received (input) |
| `C1_extract/` | A plain unzip that was already present before the session; left untouched |
| `C1/` | C1 imported with `capsule-maker import` and verified |
| `.capsule-maker-src/`, `.venv/` | Capsule-Maker source and the Python environment |
| `nlcc_tx/` | NLCC thioxanthone study: inputs, dry runs, runs, analysis, `RESULTS.md` |
| `capsule_build/` | Curation script, memory and report for the new capsule |
| `C1-portability-check-claude/`, `.zip` | New capsule, child of C1, approved by LiiiiTx, exported; SHA-256 `ce035b22…3f00` |
| `conversation_log/` | Per-round logs, `QUESTIONS.md`, `round_stats.py` |
| `TESTBED.md` | This file |

---

## 6. Differences from C1's environment that matter for reproduction
1. **Hardware:** one Xeon workstation (Intel, AVX-512) instead of an AMD EPYC cluster. The energies agree to below 10⁻⁸ Ha, but timings and memory are not directly comparable (record `pc-cost`).
2. **BigDFT build:** a local 1.9.5.221 build with bundled PSolver 1.9, instead of the cluster module `bigdft/rho0` with PSolver 1.10.
3. **Slurm:** a single node with no task plugin. Launch with `mpirun --bind-to none` and no `module load bigdft`.
4. **PyBigDFT:** 1.9.6.1 instead of 1.9.6, with the same `set_psp_nlcc` and `run_dir` behaviour (records `pc-psp-api-confirmed`, `pc-fail-rundir`).
5. **Agent:** the same model family as C1's curation (Claude Opus 5.5), but a fresh session with no access to the original conversations.
