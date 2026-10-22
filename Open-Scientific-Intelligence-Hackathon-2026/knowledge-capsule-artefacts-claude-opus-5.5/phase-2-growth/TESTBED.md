# Testbed: BigDFT ΔSCF triplet energy of 6a on TSUBAME4.0

Continuation of research capsule **C1** (Capsule-Maker), Phase 2 onward: reproduce the
experimental triplet energy E_T(6a) = 269 kJ/mol (2.79 eV) of the photocatalytic tetrapeptide 6a
(Irle et al., *Nature Synthesis* 2026) with BigDFT ΔSCF. Success criterion (capsule record
`dec-criteria-ok`): PBE0 adiabatic ΔSCF E_T within 2.79 ± 0.15 eV.

Last updated: 2026-10-22 (JST). Status values below are a snapshot of that date.

## 1. Models

### 1.1 Scientific model

| Item | Setting | Source |
|---|---|---|
| Method | ΔSCF, wavelet DFT (BigDFT), free (isolated) boundary conditions | capsule `proc-inputs` |
| System | 6a = (R,R,S)-Pga-Pro-Aib-pTxa-OMe, C31H34N4O7S, 77 atoms, neutral, 226 electrons | `dec-state` |
| Start geometry | S1 (`inputs/6a_S1.xyz`): GFN2-xTB/ALPB(CH2Cl2) with NMR (Table S1) flat-bottom restraints | `dec-select-ok`, `res-s1` |
| States | S0: closed shell (nspin 1). T1: lowest triplet as spin-polarised ground state (nspin 2, mpol 2) | `proc-inputs` |
| Functionals | PBE (libxc, ixc -101130); PBE0 (ixc -406, exact exchange with OP2P) | `dec-psp-ok`, `res-tx-pbe0` |
| Pseudopotentials | Goedecker–Krack HGH-K, PBE-generated, for C, H, N, O, S (also used with PBE0) | `dec-psp-ok` |
| Production grid | hgrid 0.35 bohr, rmult (6, 9); verified by the Phase 2 grid study (§5) | this work |
| SCF convergence | gnrm_cv 1e-5. T1: itermax 200, nrepmax 5 (default 50/1 does not converge, §5) | this work |
| Geometry optimisation | SQNM, ncount_cluster_x 300, betax 1.0, forcemax 2e-4 Ha/bohr (thioxanthone protocol) | `proc-inputs` |
| Constrained variant | Only thioxanthone moves: atoms 28–42 and their H 70–76 (0-based, 22 atoms); other 55 atoms `Frozen: fxyz` | this work (option A) |
| Corrections not included | zero-point, vibronic, solvent | `q-zpe`, `q-conditions` |

### 1.2 AI agents and tooling

| Role | Model / tool | Version |
|---|---|---|
| Capsule creator (sessions b8d95464, e3e745d8) | Claude Opus 5.5 in Claude Code | per capsule `SUMMARY.md` |
| This continuation | Claude Opus 5.5 (`claude-opus-5-5`) in Claude Code | Claude Code 2.1.308 |
| Capsule handling | Capsule-Maker CLI, main @ `4a37abe` (2026-10-14) | package 0.1.0a1 |
| Cluster access | Claude Code plugin `tsubame@tsubame-marketplace` (tsubame-hpc, tsubame-docs MCP servers) | 0.1.0 |

## 2. Local environment (workstation)

| Item | Value |
|---|---|
| OS | Ubuntu 24.04.4 LTS, Linux 7.0.0-28-generic x86_64 |
| CPU | Intel Xeon w7-3565X, 1 socket, 32 cores / 64 threads |
| Memory | 251 GiB |
| GPU | NVIDIA GeForce RTX 3050 6 GB (not used; NVML driver/library mismatch at time of writing) |
| Python | 3.12.9 (miniconda) |
| Capsule-Maker venv | `../.venv`: capsule-maker 0.1.0a1, jsonschema 4.26.0, numpy 2.5.4, mcp 1.30.0 |
| Local role | capsule import/verify/resume; job preparation, monitoring (SSH), log analysis. No BigDFT runs locally. |

## 3. Remote environment: TSUBAME4.0

### 3.1 Hardware

| Item | Value |
|---|---|
| Site | TSUBAME4.0, Institute of Science Tokyo (login.t4.gsic.titech.ac.jp) |
| Node | HPE Cray XD665: 2 × AMD EPYC 9654 (192 cores), 768 GB DDR5, 4 × H100 SXM5 94 GB, 1.92 TB NVMe |
| Interconnect | InfiniBand NDR200 × 4 |
| Scheduler | Altair Grid Engine; jobs sized by resource type, max wall time 24 h |
| GPUs | not used (BigDFT build is CPU-only in these runs) |

Resource types used:

| Type | Cores | Memory | Used for |
|---|---|---|---|
| `cpu_16` | 16 | 36.8 GB | dry runs (free trial) |
| `cpu_80` | 80 | 184 GB | PBE single points, geometry optimisations (20 MPI × 4 OMP) |
| `cpu_160` | 160 | 368 GB | first free-geopt submission (never started; cancelled) |
| `node_f` | 192 + 4 GPU | 768 GB | PBE0 single points (24 MPI × 8 OMP) |

### 3.2 Software

| Item | Value |
|---|---|
| BigDFT build | `~/local/bigdft_rho0/build/install` (built 2025-11-11) |
| Library versions | libbigdft 1.9.5-dirty, PSolver 1.10, futile 1.9, CHESS 0.2.4, libxc 4.3.4, NTPoly 3.1.0, libyaml 0.2.5 |
| Compiler / MPI | GCC (gfortran), OpenMPI 5.0.7-gcc |
| Modules | `cuda/12.8.0`, `openmpi/5.0.7-gcc`, `intel/2025.0.0` (+ UCX 1.16.0 LD_PRELOAD, `OMPI_MCA_coll=^hcoll`) |
| Python (conda env `bigdft`) | Python 3.12.12, PyBigDFT 1.9.6.0, numpy 2.3.4, PyYAML 6.0.3 |
| Launch | `mpirun -np N --map-by slot:PE=OMP bigdft -n NAME` (not srun; capsule `fail-srun`) |
| Environment script | `scripts/env/bigdft_env.sh` (mirrors the user's `~/scripts/Tsubame_pyBigdft.sh`) |

The library versions match the capsule's compute environment (`ctx-env`) exactly.

### 3.3 Accounts, storage, points

| Item | Value |
|---|---|
| User | `uu04438` |
| Group charged | `tga-enii402-2025` (plugin default); other groups: tga-imlab, tga-2024ENII402, tga-imlabCASB2 |
| Points (`t4-user-info group point`) | start of session: `0.86 / 721.01`; 2026-10-22 ~17:30: `150.94 / 570.82` (columns as printed; the first column is presumably points in use/reserved, not verified) |
| Free trial runs | no group: ≤ 2 units, 3 min. Used for all smoke tests and dry runs |
| Remote project dir | `/home/8/uu04438/projects/capsule-6a-ET` (27 GB; 18 GB of it wavefunctions in `runs_wf`) |
| Home quota | 125 GB; 49 GB used before this work |

## 4. Layout of this directory

```
bigdft-6a-tsubame/
├── TESTBED.md                  this document
├── inputs/                     BigDFT YAML inputs (self-contained: dft, geopt, posinp, psppar)
│   ├── 6a_S1.xyz, 6a_S3.xyz    start geometries from the capsule
│   ├── 00_phase2_grid_pbe/     24 capsule inputs: S0/T1 at S1, hgrid 0.45–0.30 × rmult (5,8)–(7,10)
│   ├── 01_t1_scf_rerun/        12 T1 inputs + itermax 200, nrepmax 5
│   ├── 02_pbe_s1_wavefunctions/ S0/T1 PBE at S1 (h0.35 r6-9) + output: {orbitals: binary}
│   ├── 03_pbe0_s1_vertical/    S0/T1 PBE0 at S1, inputpsiid 2 (restart from 02)
│   │   └── superseded_cold_start/  first PBE0 inputs (input guess); job cancelled before start
│   ├── 04_geopt_free/          unconstrained PBE geopt of S0/T1 from S1
│   └── 05_geopt_constrained/   PBE geopt, thioxanthone only (55 atoms frozen), restart from 02
├── scripts/
│   ├── env/bigdft_env.sh       module/conda/library setup sourced by every job
│   ├── jobs/                   run_array.sh (array runner), run_array_rst.sh / run_array_rst2.sh
│   │                           (copy a converged data dir, then restart), memwatch.sh (memory log)
│   ├── checks/                 dryrun_dir.sh (memory-estimation dry run of a directory),
│   │                           smoke_test.sh, restart_test.sh, restart_test2.sh
│   └── lists/                  array task lists (one input name per line; *_rst2 lists "NAME SRC")
├── results/                    logs copied back from TSUBAME (wavefunction data-* dirs excluded)
│   ├── 00_ … 05_               one sub-directory per run, same names as inputs
│   ├── dryruns/                bigdft-tool memory-estimation output per stage
│   ├── checks/                 smoke launch and restart test
│   └── joblogs/                Grid Engine <job>.o<id>/.e<id> files
└── analysis/
    ├── analyze_6a.py           stdlib log parser: energies, SCF convergence, ΔE table
    ├── phase2_grid_pbe_50iter.json      first Phase 2 pass (T1 unconverged)
    └── phase2_grid_pbe_converged.json   Phase 2 with converged T1
```

Remote → local mapping: `bigdft/inputs`→`inputs/00_…`, `inputs_v2`→`01`, `inputs_wf`→`02`,
`inputs_pbe0r`→`03`, `inputs_pbe0`→`03/superseded_cold_start`, `inputs_geopt`→`04`,
`inputs_cgeopt`→`05`; `runs`, `runs_v2`, `runs_wf`, `runs_pbe0`, `runs_geopt`, `runs_cgeopt` →
`results/00…05`.

Refresh results (wavefunctions excluded):

```bash
rsync -a --exclude='data-*' --exclude='debug/' \
  login.t4.gsic.titech.ac.jp:projects/capsule-6a-ET/runs_cgeopt/ results/05_geopt_constrained/
python3 analysis/analyze_6a.py results/01_t1_scf_rerun
```

## 5. Run record

| Job ID | Name | Stage | Resources | Group | Outcome |
|---|---|---|---|---|---|
| 9098971 | smoke6a | dry run of 24 inputs + 70 s launch test | cpu_80 × 1, 3 min | trial | 24/24 dry runs OK; 16 MPI × 4 OMP launch OK |
| 9098993 | p2_6a_pbe | 00 Phase 2 grid study (24 tasks) | cpu_80, 3 h | tga-enii402-2025 | S0 converged; all T1 hit itermax 50 (gnrm 6.6e-5–1.5e-4) |
| 9099239 | dry_v2 | dry run 01 + 04 | cpu_16, trial | trial | OK |
| 9099248 | p2v2_t1 | 01 T1 reruns (12 tasks) | cpu_80, 3 h | tga-enii402-2025 | all converged < 1e-5 after 490–560 iterations |
| 9099250 | geopt6a | 04 free geopt, first submission | cpu_160, 24 h | tga-enii402-2025 | waited > 2 h in queue; cancelled (user approved) |
| 9099254 | dry_pbe0 | dry run of cold-start PBE0 | cpu_16, trial | trial | OK |
| 9099280 | pbe0_s1 | cold-start PBE0 at S1 | node_f, 24 h | tga-enii402-2025 | held, then cancelled before start (user approved) |
| 9100767, 9100803 | rst_test(2) | wavefunction write + restart test | cpu_80, trial | trial | restart converges in 2 iterations, ΔE 2e-9 Ha |
| 9100829 | dry_wf | dry run 02 + 03 | cpu_16, trial | trial | OK |
| 9100863 | wf_s1 | 02 PBE at S1 with wavefunctions | cpu_80, 3 h | tga-enii402-2025 | done; energies reproduce 00/01 |
| 9100870 | pbe0r_s1 | 03 PBE0 at S1 (restart) | node_f, 24 h | tga-enii402-2025 | queued (waiting for a full node) |
| 9100884 | geopt6a | 04 free geopt S0/T1 | cpu_80, 24 h | tga-enii402-2025 | running |
| 9101302 | dry_cgeo | dry run 05 | cpu_16, trial | trial | OK, 55 frozen atoms parsed |
| 9101308 | cgeopt6a | 05 constrained geopt S0/T1 | cpu_80, 24 h | tga-enii402-2025 | running |

Every input was dry-run (bigdft-tool memory estimation) before any calculation (capsule `dec-dryrun-first`).

## 6. Results so far

| Quantity | Value | Status |
|---|---|---|
| PBE vertical E_T at S1, grid study | 2.5114–2.5126 eV across 12 grids (1.2 meV spread) | final |
| PBE vertical E_T at S1, h0.35 r(6,9) | 2.5120 eV = 242.37 kJ/mol (target 2.79 eV: −0.278 eV) | final |
| Same, first pass with T1 capped at 50 iterations | 2.547 eV (35 meV too high) | superseded |
| PBE adiabatic E_T, constrained (option A) | — | running (9101308) |
| PBE adiabatic E_T, free | — | running (9100884) |
| PBE0 vertical E_T at S1 | — | queued (9100870) |
| PBE0 adiabatic E_T (success criterion) | — | after geopts |

## 7. Known issues and deviations

- **T1 SCF convergence.** The 6a triplet stagnates at gnrm ≈ 1e-4 with BigDFT defaults; it needs
  ~500 iterations (itermax 200, nrepmax 5). Spin-down frontier occupied levels are closely spaced
  (likely peptide lone pairs). Related to the capsule's open question `q-t1-character`.
- **PBE0 initial guess.** PBE0 restarts from converged PBE wavefunctions (`inputpsiid: 2`), unlike the
  thioxanthone calibration (input guess). This changes only the starting point, not the converged
  state, and keeps the T1 state consistent with PBE.
- **Hybrid memory.** Dry runs underestimate PBE0 memory (capsule `fail-pbe0-oom`); the PBE0 job logs
  node memory every 20 s (`memwatch.log`).
- **Job log side effect.** `run_array.sh` was edited while job 9099248 was executing it; those tasks'
  `.o` files lack the post-run `end`/timing lines. BigDFT logs are complete.
- **Disk.** `runs_wf` (18 GB) and `restart_test` (2.8 GB) on TSUBAME hold wavefunctions; the latter
  can be removed once no longer needed.
- **Dry-run checker.** The first version of `dryrun_dir.sh` flagged "error" in parameter
  descriptions; fixed to check BigDFT error blocks and the presence of the memory estimate.
