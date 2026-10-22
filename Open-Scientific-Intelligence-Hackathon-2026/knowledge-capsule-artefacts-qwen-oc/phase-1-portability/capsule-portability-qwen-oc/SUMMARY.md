# Research Capsule

Continue the OSI-2026 portability trial carried in this OpenCode/Qwen session: the verified C1 handover state, the thioxanthone PBE/NLCC triplet-energy result (241.21 kJ/mol) with its reproduction procedure and evidence, the runtime and trust-boundary decisions, and the open 6a question.

Origin: opencode-session — OpenCode chat session <session-1> (model Qwen3.8-27B via llama.cpp) in /home/user/Work/osi-hackathon-2026, 2026-10-21; consolidated manually from the session conversation log and the OpenCode session database

## Knowledge

### c1-state (result, verified)

C1 state at resume (capsule-maker resume C1; 63 records): goal = reproduce E_T(6a) = 269 kJ/mol (2.788 eV) with BigDFT Delta-SCF. Phase 0 done: structures S1/S2/S3, 26 dry-run-validated inputs. Phase 1 done: thioxanthone calibration - PBE adiabatic E_T 236.70 kJ/mol (-37.4 vs literature 274.1, fails the 0.2 eV window); PBE0 260.75 kJ/mol (-13.35, passes). Next: the 6a phases (24 dry-run-validated S1 PBE S0/T1 inputs, then PBE0 single points; acceptance within +/-0.15 eV of 2.79 eV).

Evidence: ev-c1-resume, ev-session-log
Provenance: src-c1, src-oc-session
Supersedes: none

### context-host (context, verified)

Host facts established in-session: 24 cores / 62 GB RAM Linux; no Docker daemon or CLI, no podman/nerdctl/ctr/umoci (skopeo present), sudo requires a password (no root); jhbuild-built BigDFT 1.9.5.680-739eea at /home/user/Work/build/install/bin/bigdft (suite devel @ 739eeadcc); PyBigDFT pseudopotential Database at /home/user/Work/build/PyBigDFT/lib/BigDFT/Database/psppar with families Krack (LDA, PBE; HGH-K) and SS (HGH-K + NLCC, Saha 2015) - the SS set covers C/H/N/O and others but has no S. Thioxanthone-scale PBE jobs fit the host comfortably.

Evidence: ev-session-log
Provenance: src-oc-session, src-bigdft-build
Supersedes: none

### dec-protocol (decision, verified)

Protocol held identical to C1 Phase 1 PBE calibration: PBE, hgrid 0.35 bohr, rmult (6,9), gnrm_cv 1e-5, free boundary conditions, T1 = nspin 2 / mpol 2 (magnetization 2.000), fixed-geometry Delta-SCF single points at C1's PBE-optimized S0 and T1 geometries (no re-optimisation, per user instruction).

Evidence: ev-nlcc-runs
Provenance: src-c1, src-oc-session
Supersedes: none

### dec-psp-nlcc (decision, verified)

Two-step psppar setup (user instruction): first set capsule C1's psppar (Krack PBE HGH-K, XC 11; byte-identical to PyBigDFT Database Krack/PBE files) for all elements C/H/O/S, then set the NLCC psppar (Database SS set, type HGH-K + NLCC, Saha 2015, psp XC field -101130), overwriting where available. Result: C, H, O -> NLCC; S -> no NLCC entry in the SS set -> keeps C1's Krack PBE HGH-K. Electron count verified 72 e- in both generated inputs.

Evidence: ev-nlcc-runs
Provenance: src-c1, src-oc-session
Supersedes: none

### dec-runtime-local (decision, verified)

Runtime choice: the bigdft-runtime capsule's Docker path is not executable on this host (fail-docker), so the locally jhbuild-built BigDFT 1.9.5.680-739eea was used - closer to C1's 1.9.5 module than the capsule's 1.9.1 image. The runtime was validated first with the capsule's own H2/LDA smoke input and pass criteria: EKS -1.13672072759955523 Ha (capsule recorded -1.1367207275995557; pass range (-2, -0.5) Ha), gradient 7.2e-5 <= 1e-4 -> PASS before any production run.

Evidence: ev-nlcc-runs, ev-session-log
Provenance: src-bigruntime, src-bigdft-build, src-oc-session
Supersedes: none

### ev-c1-resume (evidence, verified)

capsule-maker resume C1 output: the capsule goal plus all 63 knowledge records (goal + records JSON), the starting point carried into this session.

Evidence: none
Provenance: src-c1
Supersedes: none

### ev-nlcc-runs (evidence, verified)

As-run artifacts of the NLCC thioxanthone calculation: the two generated PBE single-point inputs (embedded psppar: C/H/O = SS HGH-K + NLCC Saha 2015, S = Krack PBE HGH-K; PBE-optimized geometries from C1), the H2/LDA runtime-smoke input and its BigDFT log, the S0/T1 BigDFT 1.9.5.680 log and time files, the two packaged scripts (make_inputs.py, analyze.py), and result.json (E_S0, E_T1, E_T, C1 comparison, magnetization and XC-warning checks).

Evidence: none
Provenance: src-oc-session, src-bigdft-build
Supersedes: none

### ev-session-log (evidence, verified)

Full per-round conversation log of the session (rounds 1-6 as staged; the capsule-creation round continues in the live workspace log) with verbatim prompts and outputs, per-round wall time, and per-model-call token tallies from the OpenCode session database; plus the live question sheet (Q1-Q6 as staged).

Evidence: none
Provenance: src-oc-session
Supersedes: none

### fail-docker (failed_attempt, verified)

Attempted execution via the bigdft-runtime capsule's documented Docker runtime (pinned image bigdft/runtime@sha256:6f16f65f5b33ffe83e53d3c228c21a1e8eb97d0b426f4fad0c805d0bc0540336, BigDFT 1.9.1, 2021): no docker CLI on PATH, no /var/run/docker.sock, no podman/nerdctl/ctr/umoci container runtime, sudo requires a password (no root); image layers cannot be executed without a runtime (skopeo can inspect but not run). Resolved by dec-runtime-local.

Evidence: ev-session-log
Provenance: src-bigruntime, src-oc-session
Supersedes: none

### open-6a (question, unresolved)

Open (from C1, carried forward): proceed with the 6a phases - run the 24 dry-run-validated S1 PBE S0/T1 inputs, then PBE0 single points at the converged PBE geometries, adiabatic Delta-SCF E_T, acceptance within +/-0.15 eV of 2.79 eV, S3 as the sensitivity check. The user's earlier next-step question was dismissed in-session. The local BigDFT 1.9.5.680 runtime is now established and smoke-validated on this host, so a local continuation is feasible; C1 sizing note: 6a T1 up to ~48 GB serial (fits the 62 GB host).

Evidence: none
Provenance: src-c1, src-oc-session
Supersedes: none

### proc-repro (procedure, verified)

Reproduction procedure (packaged scripts): (1) python make_inputs.py - builds the two PBE single-point inputs from C1 Phase 1b single-point templates with the two-step psppar merge (C1 Krack PBE for all elements, then SS NLCC overwrite where available); asserts 72 electrons. (2) Per run directory: bigdft -n NAME with NAME.yaml present, ulimit -s unlimited, OMP_NUM_THREADS=12 (24-core host; the S0/T1 pair can run in parallel). (3) python analyze.py - parses the final EKS from the BigDFT logs, computes E_T in Ha/eV/kJ (1 Ha = 27.211386248 eV = 2625.497 kJ/mol), compares to C1, writes result.json. Expected at BigDFT 1.9.5.680: E_T = 0.09187212770955 Ha (241.21 kJ/mol).

Evidence: ev-nlcc-runs
Provenance: src-oc-session
Supersedes: none

### res-nlcc-et (result, verified)

Thioxanthone adiabatic Delta-SCF triplet energy, PBE + NLCC psppar (C/H/O NLCC Saha 2015, S Krack PBE), at C1 PBE-optimized geometries, BigDFT 1.9.5.680-739eea, 12 OpenMP threads per run (parallel pair, 24-core host): E(S0) = -116.849975510618592 Ha (24 SCF iterations, gnrm 6.7e-6); E(T1) = -116.758103382909042 Ha (33 iterations, gnrm 1.0e-5, magnetization 2.000). E_T = 0.09187212770955 Ha = 2.49997 eV = 241.21 kJ/mol. Versus C1 PBE/Krack 236.70 kJ/mol (0.09015353 Ha): +4.51 kJ/mol (+0.047 eV) with the NLCC class. Versus literature 274.1 kJ/mol: -32.9 kJ/mol (-0.34 eV), still outside the 0.2 eV calibration window; the deficit remains functional-dominated (C1 PBE0 = 260.75 kJ/mol). Absolute KS energies sit ~11.9 Ha below C1's and are not comparable across pseudopotential classes (different core treatments); only the Delta-E is meaningful. No XC-mismatch warnings in either BigDFT log.

Evidence: ev-nlcc-runs
Provenance: src-oc-session, src-bigdft-build
Supersedes: none

### session-overview (context, verified)

OSI-2026 portability trial: an OpenCode harness session running Qwen3.8-27B (llama.cpp) in /home/user/Work/osi-hackathon-2026. Rounds 1-6 (full verbatim log packaged as evidence): (1) inventory of tools available to the agent; (2) established per-round conversation logging (prompt, output, time, tokens) with a live question sheet; (3) installed capsule-maker v0.1.0-alpha (uv venv, [science,mcp] extras), imported and integrity-verified C1.zip (131 files), installed C1's declared Python dependencies, and resumed from C1 (63 knowledge records), treating C1 content strictly as untrusted data; (4) full 12-section description of the C1 knowledge base; (5) completed the conversation log with verbatim outputs; (6) re-ran the thioxanthone PBE triplet energy with the NLCC pseudopotential class on C1's PBE-optimized geometries using the local BigDFT runtime (see res-nlcc-et). Round 7 (creation of this capsule) continued in the live workspace log after staging.

Evidence: ev-session-log
Provenance: src-oc-session
Supersedes: none

### trust-boundary (decision, verified)

Standing rule (user, rounds 2-3): capsule contents (C1.zip, bigdft-runtime.zip) are untrusted data - no executing capsule code, no --trust-code, in-capsule instructions treated as data only. Applied throughout: C1 tests/procedures never executed; C1 psppar files and PBE-optimized geometries used only as inert input data for the calculations the user explicitly ordered.

Evidence: ev-session-log
Provenance: src-oc-session
Supersedes: none

## Source references

- src-bigdft-build: file:///home/user/Work/build/install/bin/bigdft — Locally jhbuild-built BigDFT 1.9.5.680-739eea (suite devel @ 739eeadcc), the executable runtime on this host
- src-bigruntime: file:///home/user/Work/osi-hackathon-2026/bigdft-runtime.zip — Imported bigdft-runtime capsule (documented Docker BigDFT 1.9.1 runtime), 19 files, integrity verified on import
- src-c1: file:///home/user/Work/osi-hackathon-2026/C1.zip — Imported research capsule C1 (thioxanthone/6a BigDFT Delta-SCF study), 131 files, integrity verified on import
- src-oc-session: opencode-session://<session-1> — OpenCode chat session (model Qwen3.8-27B via llama.cpp) in /home/user/Work/osi-hackathon-2026, 2026-10-21; consolidated manually from the session conversation log and the OpenCode session database

## Conflicts

None declared or detected.

## Environment

Python >=3.10
- pyyaml>=6.0

## Receiving instructions

Inspect the manifest, knowledge, evidence, procedures, and tests before approval.
Verify integrity and environment requirements. Import/inspection never run code.
Run tests only after explicit trust using `capsule-maker verify PATH --trust-code`.
Checksums establish integrity, not authorship or scientific validity.
