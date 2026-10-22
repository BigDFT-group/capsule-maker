# Phase 2 run record (TSUBAME4.0, 2026-10-22 JST)

All jobs used the bigdft_rho0 build (libbigdft 1.9.5, PSolver 1.10, futile 1.9, CHESS 0.2.4,
libxc 4.3.4, GCC + OpenMPI 5.0.7) with `phase2/scripts/bigdft_env.sh`, launched as
`mpirun -np N --map-by slot:PE=OMP bigdft -n NAME`. "trial" = free TSUBAME trial run (no group,
≤ 2 units, 3 min). Points were charged to one project group (identity not packaged).

| Job | Stage | Resources | Outcome |
|---|---|---|---|
| 9098971 | smoke test: dry run of the 24 C1 Phase 2 inputs + 70 s launch | cpu_80, trial | 24/24 dry runs OK; 16 MPI × 4 OMP launch, 226 electrons |
| 9098993 | 00 grid study, 24 single points at S1 | cpu_80 × 24, 20 MPI × 4 OMP | S0 converged; every T1 stopped at itermax 50 (gnrm 6.6e-5–1.5e-4) |
| 9099239 | dry run 01 + 04 | cpu_16, trial | OK |
| 9099248 | 01 T1 reruns, itermax 200, nrepmax 5 | cpu_80 × 12 | all converged (490–560 iterations, 15 min – 1 h 37 min) |
| 9099250 | 04 free geopt, first submission | cpu_160 | > 2 h in queue; cancelled before start (researcher approved) |
| 9099254 | dry run of cold-start PBE0 at S1 | cpu_16, trial | OK |
| 9099280 | cold-start PBE0 at S1 | node_f | held, then cancelled before start (researcher approved) |
| 9100767 | restart test, wavefunction files only | cpu_80, trial | failed: data-NAME/glr.dat missing |
| 9100803 | restart test, full data dir | cpu_80, trial | converged in 2 iterations, ΔE 2e-9 Ha |
| 9100829 | dry run 02 + 03 | cpu_16, trial | OK |
| 9100863 | 02 PBE at S1 writing wavefunctions | cpu_80 × 2 | done; energies reproduce 00/01 |
| 9100870 | 03 PBE0 at S1, restart from 02 | node_f, 24 MPI × 8 OMP | queued (waiting for a full node) at packaging time |
| 9100884 | 04 free geopt S0/T1 | cpu_80 × 2 | S0 converged (86 steps); T1 cancelled after ~108 steps (researcher request) |
| 9101302 | dry run 05 | cpu_16, trial | OK, 55 frozen atoms parsed |
| 9101308 | 05 constrained geopt S0/T1, restart from 02 | cpu_80 × 2 | S0 68 steps, T1 94 steps, both converged |
| 9102448 | restart from S1 wavefunctions at the cgT1 geometry | cpu_80, trial | runs but poor guess (iteration 1: −337.7 Ha, gnrm 0.78) |
| 9102458 | dry run 07 | cpu_16, trial | OK |
| 9102490 | dry run 06 | cpu_16, trial | OK |
| 9102502 | 06 PBE at cgS0/cgT1 writing wavefunctions (4 tasks) | cpu_80 × 4 | S0 tasks done; T1 tasks running at packaging time |
| 9102503 | 07 PBE0 at cgS0/cgT1, restart from 06 (4 tasks) | node_f × 4, 24 MPI × 8 OMP | waiting for 9102502 at packaging time |

Stage numbers match `phase2/inputs/NN_*.yaml`. Stage 00 inputs are C1's `bigdft/inputs/6a_S1_*`.
Full logs are in the external archive `phase2-results-logs-20261022` (see manifest); each run's
log SHA-256 is in `energies.json`.
