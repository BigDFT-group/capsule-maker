# Phase 2 (6a) — Job Situation Report

**Report date:** 2026-10-22 (all events 2026-10-21; times UTC)
**Status:** all jobs cancelled on user instruction; **nothing running**; host idle.

## 1. Current situation

- No BigDFT jobs running; scheduler process stopped.
- Host (AMD Ryzen 9 5900X: 12 physical cores × HT = 24 HW threads, 62 GB RAM) is free (~46 GB available at the time of cancellation).
- All partial run artifacts are preserved under `phase2_6a/` (see §6); nothing deleted.
- The PBE0 queue (pair + fallback chain) remains configured in `phase2_6a/scheduler.py`; the 24 PBE grid inputs remain staged in `phase2_6a/runs/`.

## 2. Timeline (2026-10-21)

| Time (UTC) | Event |
|---|---|
| 15:14 | User instruction: run Phase 2 (24-run PBE grid on 6a S1, then PBE0 single points, compare vs 2.79 ± 0.15 eV) |
| 16:06:50 | Scheduler launched; PBE S0 + T1 `h0.45_r5-8` started (12 OMP threads each); 28 jobs queued |
| 18:49–18:55 | Progress check: S0 iter 18 (gnrm 4.9e-5), T1 iter 6 (gnrm 5.7e-3); no completions |
| 19:03 | User: "too slow — cancel" |
| ~19:40 | 24-run PBE grid killed (at snapshot 19:39:24: S0 iter 22, T1 iter 8) |
| 19:45 | User instruction: just the triplet-energy calculation (PBE0 pair); queue reduced to 6 PBE0 jobs |
| 20:00:57 | PBE0 S0 `h0.35_r6-9` launched (24 MPICH ranks) — attempt 1 |
| ~20:13 | Attempt 1 cancelled: RSS monitor found broken (§5.1) |
| 20:23:24 | PBE0 S0 relaunched under fixed monitor — attempt 2 |
| 21:06:10 | User: "kill the job" — PBE0 killed; scheduler stopped; all jobs down |

## 3. Per-job state at kill

| Job | Runtime | Elapsed | Progress at kill | Memory |
|---|---|---|---|---|
| `6a_S1_S0_pbe_h0.45_r5-8` | OMP 12 thr | 3 h 32 min | iter 22, EKS −358.77176926 Ha, gnrm 1.05e-5 (target 1e-5, ~1–3 iters short; ΔE already < 4.3e-8 Ha/iter) | RSS 4.49 GB (dry-run est. 4.31) |
| `6a_S1_T1_pbe_h0.45_r5-8` | OMP 12 thr | 3 h 33 min | iter 8, EKS −358.67532370 Ha, gnrm 2.15e-3 (early; ΔE ≈ −1.9e-3 Ha/iter) | RSS 8.79 GB (est. 8.57) |
| 22 other PBE grid jobs | — | never launched | — | — |
| `6a_S1_S0_pbe0_at_S1_h0.35_r6-9` (attempt 1) | MPI 24 ranks | ~13 min | setup / input-guess phase, **0 SCF iterations** | 4.41 GB tree RSS (measured ~11 min in) |
| `6a_S1_S0_pbe0_at_S1_h0.35_r6-9` (attempt 2) | MPI 24 ranks | 42 min 46 s | setup / input-guess phase, **0 SCF iterations** | tree RSS 1.57 GB (1 min) → 4.41 GB (36 min) |
| 5 other PBE0 jobs (T1@h0.35 + fallback chain) | — | never launched | — | — |

**Completed jobs: 0. No valid E_T was produced.**

Non-converged diagnostic (NOT a result): at the kill snapshot, E(T1, iter 8) − E(S0, iter 22) = 0.09645 Ha ≈ 2.62 eV ≈ 253 kJ/mol. S0 was essentially converged, but T1 was at iteration 8 with its energy still dropping ~2e-3 Ha/iteration, so the true PBE E_T at this grid lies *below* 2.62 eV. Do not quote as a result.

## 4. Why it was slow (measured, not estimated)

| Anchor (measured on this host) | Rate |
|---|---|
| PBE S0, `h0.45_r5-8` (480k grid points), 12 threads | ~8.6–9 min/iter (22 iters in 213 min) |
| PBE T1, same grid, 12 threads | ~24 min/iter (average at iter 8) |
| Per-iter scaling | ∝ grid points → T1 ≈ 60–65 min/iter at `h0.35_r6-9` (1.30M pts), ≈ 2 h/iter at `h0.30_r7-10` (2.61M) |
| PBE0 | thioxanthone-measured hybrid ratio ≈ 2–3× PBE per iter; 6a setup/input-guess phase > 43 min with **zero** SCF iterations in either attempt |

Context: the two 12-thread PBE jobs already saturated all 12 physical cores (CPU scaling observed at ~57 % of max). T1 SCF needs ~40–60 iterations at the fine grids.

Resulting pre-cancellation estimates:
- **Full 24-run grid:** ~29,000–31,000 core-min ≈ **2–3 weeks wall** (T1 at fine grids dominates).
- **Minimal PBE0 pair at `h0.35_r6-9`:** S0 ≈ 1–2.5 d + T1 ≈ 4–10 d → **E_T in ≈ 6–12 days** (T1 is the long pole: hybrid, spin-polarized, largest grid).
- New unknown exposed by the attempts: the PBE0 **setup/input-guess phase** for 6a has not finished in 56 min cumulative — on thioxanthone (72 e⁻) it was short, so the 6a guess cost is the least-quantified part of the budget.

## 5. Issues found and disposition

1. **Scheduler RSS monitor bug (fixed).** MPICH/hydra puts each rank in its own process group; the scheduler scanned by pgrp and therefore only saw `mpiexec` (0.0 GB) — the 40 GB probe-kill threshold could never fire. Fix in `scheduler.py`: monitor the full process tree via ppid (verified live: 24 ranks, real RSS), plus a 60 s grace to absorb the transient input-guess peak (where C1's thioxanthone PBE0 peaked on the cluster). Attempt 1 was cancelled; attempt 2 ran under the fixed monitor (peak tree RSS 4.41 GB — the threshold was never close).
2. **PBE0 setup phase unexpectedly long** (see §4) — the dominant new time-budget risk for any hybrid run on 6a here.
3. **Docker runtime unavailable on this host** (established fact; bigdft-runtime capsule documents the Docker path). Execution used local BigDFT 1.9.5.680-739eea (MPICH-linked). H2/LDA capsule smoke test passed in both OMP (1 thread) and MPI (4 ranks) configurations: EKS −1.13672072759955 Ha, final gnrm 7.2e-5, exit 0.
4. **Operational:** during the cancellation cycle, one `pkill` pattern self-matched the invoking shell (the script text itself contained the target string), killing the shell mid-script. No job damage; subsequent kills were pid-based only.

## 6. Artifacts and how to resume

Under `phase2_6a/`:
- `runs/` — 24 staged PBE inputs; 2 partial logs (S0/T1 `h0.45_r5-8`, no `#FINAL`). Re-running a job in its directory overwrites the log.
- `pbe0/runs/` — 6 PBE0 inputs (S0/T1 × h0.35/h0.40/h0.45 `_r6-9`, generated from the C1 templates with ixc PBE→PBE0); 1 partial log (S0@h0.35).
- `scheduler.py` — patched, syntax-checked; queue = PBE0 pair + fallback chain (PBE grid dropped per the 19:45 instruction). Relaunch from `phase2_6a/`: `setsid nohup python3 scheduler.py > scheduler.out 2>&1 &`
- `analyze.py` — builds the E_T table + 2.79 ± 0.15 eV comparison once logs exist.
- `smoke/`, `smoke_mpi/` — H2/LDA validation runs (OMP and MPI).
- `progress.json`, `scheduler.log`, `scheduler.out` — full run history.

Options if resumed:
- **Cluster (preferred, if accessible):** C1's Phase 1 used Slurm with modules `openmpi/5.0.7` + `bigdft/rho0` (template: `C1/procedures/run_bigdft.slurm`; launch `mpirun -np $SLURM_NTASKS --map-by slot:PE=$OMP_NUM_THREADS bigdft -n NAME`). At 64+ threads the PBE0 pair is a matter of hours (thioxanthone PBE0 T1, 72 e⁻, took 37–38 min at 8×8).
- **Local minimal:** PBE0 pair at `h0.35_r6-9` (~6–12 days, long pole T1). Optional speed-up: `gnrm_cv` 1e-5 → 1e-4 (energy impact ~1e-6 Ha; cuts iterations ~25–35 %).
- **Local reduced:** PBE0 at `h0.40_r6-9`/`h0.45_r6-9` (coarser, cheaper, documented deviation from the endorsed grid).

## 7. Compute consumed

| Segment | Elapsed (wall) | Threads | Core-hours |
|---|---|---|---|
| PBE S0+T1 `h0.45_r5-8` (16:06:50 → ~19:39) | 3 h 33 min | 2×12 | ~85 |
| PBE0 S0 attempt 1 (20:00:57 → ~20:13) | ~13 min | 24 | ~5 |
| PBE0 S0 attempt 2 (20:23:24 → 21:06:10) | 42 min 46 s | 24 | ~17 |
| Smoke + overhead | ~5 min | ≤4 | <1 |
| **Total** | **~3 h 50 min wall** | | **~107–108 core-hours; 0 completed jobs** |

Of the PBE0 time, all of it was setup/input-guess phase (no SCF iterations in either attempt).
