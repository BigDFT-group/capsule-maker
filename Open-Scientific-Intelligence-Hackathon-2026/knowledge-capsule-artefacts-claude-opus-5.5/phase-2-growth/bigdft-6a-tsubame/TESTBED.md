# Testbed: BigDFT ΔSCF triplet energy of 6a on TSUBAME4.0

Continuation of research capsule **C1** (Capsule-Maker), Phase 2 onward: reproduce the
experimental triplet energy E_T(6a) = 269 kJ/mol (2.79 eV) of the photocatalytic tetrapeptide 6a
(Irle et al., *Nature Synthesis* 2026) with BigDFT ΔSCF. Success criterion (capsule record
`dec-criteria-ok`): PBE0 adiabatic ΔSCF E_T within 2.79 ± 0.15 eV.

Last updated: 2026-10-22 ~20:20 JST. Status values below are a snapshot of that time.

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
| Points (`t4-user-info group point`) | start of session: `0.86 / 721.01`; ~17:30: `150.94 / 570.82`; ~20:10: `232.64 / 489.12` (columns as printed; the first column is presumably points in use/reserved, not verified) |
| Free trial runs | no group: ≤ 2 units, 3 min. Used for all smoke tests and dry runs |
| Remote project dir | `/home/8/uu04438/projects/capsule-6a-ET` (inputs, scripts, S1 wavefunctions `runs_wf`, earlier runs) |
| Remote work dir | `/work/8/uu04438/capsule-6a-ET` (`runs_wfcg`, `runs_pbe0c`); **counts against the same 125 GB quota as home** |
| Archive | `~/CASB2/capsule-6a-ET-archive` → `/gs/fs/tga-imlabCASB2/Elliot/...` (group disk, 2 TB quota): atomic-orbital files of `runs_wf`, copied data dirs of `runs_cgeopt`, `restart_test`, `restart_test3` (22 GB, moved 2026-10-22 ~20:15) |
| Home quota | 125 GB; 49 GB before this work, 104 GB at peak, 83 GB after archiving |

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
│   ├── 05_geopt_constrained/   PBE geopt, thioxanthone only (55 atoms frozen), restart from 02
│   ├── 06_pbe_cg_wavefunctions/ PBE S0/T1 at the constrained S0 (cgS0) and T1 (cgT1) minima,
│   │                           input guess, output: {orbitals: binary}
│   └── 07_pbe0_cg/             PBE0 S0/T1 at cgS0 and cgT1, inputpsiid 2 (restart from 06)
├── scripts/
│   ├── env/bigdft_env.sh       module/conda/library setup sourced by every job
│   ├── jobs/                   run_array.sh (array runner), run_array_rst.sh / _rst2.sh / _rst3.sh
│   │                           (copy a converged data dir, then restart; _rst3 accepts absolute
│   │                           SRCDIR), memwatch.sh (memory log)
│   ├── checks/                 dryrun_dir.sh (memory-estimation dry run of a directory),
│   │                           smoke_test.sh, restart_test.sh, restart_test2.sh, restart_test3.sh
│   └── lists/                  array task lists (one input name per line; rst2/rst3 lists "NAME SRC")
├── results/                    logs copied back from TSUBAME (wavefunction data-* dirs excluded)
│   ├── 00_ … 07_               one sub-directory per run, same names as inputs
│   ├── dryruns/                bigdft-tool memory-estimation output per stage
│   ├── checks/                 smoke launch and restart tests (restart_test3: displaced geometry)
│   └── joblogs/                Grid Engine <job>.o<id>/.e<id> files
└── analysis/
    ├── analyze_6a.py           stdlib log parser: energies, SCF convergence, ΔE table per grid
    ├── summarize.py            key energies → vertical/adiabatic E_T table, writes summary.json
    ├── summary.json            output of summarize.py (pending runs listed as null)
    ├── phase2_grid_pbe_50iter.json      first Phase 2 pass (T1 unconverged)
    └── phase2_grid_pbe_converged.json   Phase 2 with converged T1
```

Run labels: `cgS0`/`cgT1` = constrained-geopt minimum of S0/T1; `6a_cgT1_S0_pbe0_…` = S0 state at
the cgT1 geometry (vertical emission partner).

Remote → local mapping: `bigdft/inputs`→`inputs/00_…`, `inputs_v2`→`01`, `inputs_wf`→`02`,
`inputs_pbe0r`→`03`, `inputs_pbe0`→`03/superseded_cold_start`, `inputs_geopt`→`04`,
`inputs_cgeopt`→`05`, `inputs_wfcg`→`06`, `inputs_pbe0c`→`07`; `runs`, `runs_v2`, `runs_wf`,
`runs_pbe0`, `runs_geopt`, `runs_cgeopt` → `results/00…05`; `/work/…/runs_wfcg`, `/work/…/runs_pbe0c`
→ `results/06`, `results/07`.

Refresh results (wavefunctions excluded) and the summary:

```bash
R=login.t4.gsic.titech.ac.jp; W=/work/8/uu04438/capsule-6a-ET
rsync -a --exclude='data-*' --exclude='debug/' $R:$W/runs_wfcg/ results/06_pbe_cg_wavefunctions/
rsync -a --exclude='data-*' --exclude='debug/' $R:$W/runs_pbe0c/ results/07_pbe0_cg/
rsync -a --exclude='data-*' --exclude='debug/' $R:projects/capsule-6a-ET/runs_pbe0/ results/03_pbe0_s1_vertical/
python3 analysis/summarize.py
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
| 9100884 | geopt6a | 04 free geopt S0/T1 | cpu_80, 24 h | tga-enii402-2025 | S0 converged (86 steps); T1 cancelled after ~108 steps, Fmax ≈ 2.6e-3 (user request) |
| 9101302 | dry_cgeo | dry run 05 | cpu_16, trial | trial | OK, 55 frozen atoms parsed |
| 9101308 | cgeopt6a | 05 constrained geopt S0/T1 | cpu_80, 24 h | tga-enii402-2025 | both converged: S0 68 steps, T1 94 steps |
| 9102448 | rst_test3 | restart from S1 wavefunctions at cgT1 geometry | cpu_80, trial | trial | runs, but poor guess (iter 1: −337.7 Ha, gnrm 0.78); killed at 3 min while converging |
| 9102458 | dry_pbe0c | dry run 07 | cpu_16, trial | trial | OK |
| 9102490 | dry_wfcg | dry run 06 | cpu_16, trial | trial | OK |
| 9102502 | wf_cg | 06 PBE at cgS0/cgT1 with wavefunctions (4 tasks) | cpu_80, 3 h | tga-enii402-2025 | S0 tasks done (S0@cgS0 reproduces the geopt energy to 8e-9 Ha); T1 tasks running |
| 9102503 | pbe0_cg | 07 PBE0 at cgS0/cgT1, restart from 06 (4 tasks) | node_f, 24 h | tga-enii402-2025 | waits for 9102502, then for full nodes |

Every input was dry-run (bigdft-tool memory estimation) before any calculation (capsule `dec-dryrun-first`).

## 6. Results so far

| Quantity | Value | Status |
|---|---|---|
| PBE vertical E_T at S1, grid study | 2.5114–2.5126 eV across 12 grids (1.2 meV spread) | final |
| PBE vertical E_T at S1, h0.35 r(6,9) | 2.5120 eV = 242.37 kJ/mol (target 2.79 eV: −0.278 eV) | final |
| Same, first pass with T1 capped at 50 iterations | 2.547 eV (35 meV too high) | superseded |
| **PBE adiabatic E_T, constrained (option A)** | **2.3532 eV = 227.05 kJ/mol** (target: −0.437 eV); relaxation T1 −0.318 eV, S0 −0.159 eV | final |
| PBE vertical emission at cgT1 | 2.2328 eV = 215.44 kJ/mol | final |
| PBE vertical absorption at cgS0 | — | running (9102502) |
| PBE adiabatic E_T, free | ≈ 2.37 eV at cancellation (T1 not converged) | indicative only |
| Free S0 vs constrained S0 | free S0 is 0.42 eV lower (conformational drift away from the NMR model) | final |
| PBE0 vertical E_T at S1 | — | queued (9100870) |
| PBE0 adiabatic E_T, constrained (success criterion) | — | queued (9102503) |
| PBE0 vertical absorption / emission at cgS0 / cgT1 | — | queued (9102503) |

Constrained minima: only atoms 28–42 and 70–76 moved (max displacement 0.29 Å in S0, 0.56 Å in T1);
C34=O35 1.240 Å (S0) and 1.288 Å (T1), cf. thioxanthone PBE 1.236 → 1.287 Å.
`python3 analysis/summarize.py` regenerates the full table.

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
- **Displaced-geometry restart.** Restarting from S1 wavefunctions at the constrained minima gives a
  poor guess (restart_test3), so step 06 recomputes PBE wavefunctions at those exact geometries before
  the PBE0 restart. Restart at an unchanged geometry converges in 2 iterations (restart_test2).
- **Geometry convergence.** All finished geopts stopped on SQNM's force-fluctuation criterion
  (Fmax below the force noise, `frac_fluct 1.0`), with Fmax 3.3–3.8e-4 Ha/bohr rather than the nominal
  2e-4; same settings as the thioxanthone calibration.
- **Disk.** `/work` shares the 125 GB home quota. Wavefunction output (`output: {orbitals: binary}`)
  also writes atomic-orbital files (~2/3 of the size); they are not needed for restarts and were moved
  to the CASB2 archive. Do the same for `runs_wfcg` once its runs finish.
- **Dry-run checker.** The first version of `dryrun_dir.sh` flagged "error" in parameter
  descriptions; fixed to check BigDFT error blocks and the presence of the memory estimate.
