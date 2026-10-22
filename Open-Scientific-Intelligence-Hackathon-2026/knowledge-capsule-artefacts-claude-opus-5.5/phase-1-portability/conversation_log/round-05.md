# Round 05

## Prompt

perform again an identical calculation of the triplet energy for the thioxanthone but using a different class of pseudopotential, use the opted structure at PBE level, do not opt again (nlcc, to properly set nlcc pseudopotential for all elements, also the one not available, we have to first set the same psppar of capsule C1, which are available for all elements, then set nlcc. This will overwrite pseudopotential for all available nlcc elements).

## Output (status at end of round; jobs still running — final results below)

The NLCC thioxanthone jobs are queued and running on the local Slurm node. Nothing is finished yet except one control run.

- **Pseudopotentials:** each input loads C1's Krack PBE file for C, H, O and S. The PyBigDFT NLCC set (Saha 2015) then replaces C, H and O, which are the elements it covers. It has no S file, so S keeps C1's Krack file. The electron count stays at 72.
- **Geometry and settings:** the C1 PBE-optimised S0 and T1 geometries, with no new optimisation. Grid spacing, extent, convergence threshold and spin settings are the same as Phase 1.
- **Dry run:** all 10 inputs passed, on the same grid as C1.
- **Local BigDFT check:** there was no `bigdft` on PATH, so I'm using a 1.9.5 build in `~/Softwares/bigdft`, which is outside this directory (only run, not changed). A control run of C1's PBE/Krack S0 point gave −104.958932175 Ha, against C1's −104.958932176. A T1 control is running.
- **Jobs (806–814):** the T1 control, 4 PBE/NLCC and 4 PBE0/NLCC single points (S0 and T1, each at both geometries). Together they give the adiabatic and vertical values, as in C1. They run two at a time with 8 MPI × 4 OpenMP each. The PBE0 jobs have 70 GB of memory for S0 and 115 GB for T1, sized from C1's measured use.
- **Timing:** going by C1's timings, the two PBE0 T1 jobs will take longest, likely more than an hour each on this machine.

I'll run `nlcc_tx/analyze_nlcc.py` when they finish, then report the NLCC triplet energies next to C1's Krack values and log this round.

### Working notes from this round
- Files: `nlcc_tx/make_nlcc_inputs.py`, `nlcc_tx/inputs/` (10 inputs plus `index.json`), `nlcc_tx/dry_run.py` (reviewed copy of C1's), `nlcc_tx/dryrun/`, `nlcc_tx/run_bigdft.slurm`, `nlcc_tx/analyze_nlcc.py`, `nlcc_tx/runs/`.
- Dry-run memory for the controls matches C1 exactly (2044 MB for S0, 4036 MB for T1). The only warning is the PBE0 one ("PSP generated with a different XC"), the same as in C1.
- Two environment problems came up and were fixed:
  - PyBigDFT accepts only a single-level `run_dir`, so the dry run is launched from inside `nlcc_tx/`.
  - `set -u` was killing the Slurm script inside the sourced `bigdftvars.sh`; strict mode now starts after the source line.
- The log comment "DoLastRunThings triggered without convergence" is printed on every final cycle in this build (`cluster.f90:758`). The control SCF did converge (gnrm 6.8e-6, below 1e-5).

## Final results (jobs finished 2026-10-21 ~20:15 local time, reported after round 07)

All 10 runs converged. Full write-up: `nlcc_tx/RESULTS.md`; machine-readable: `nlcc_tx/nlcc_summary.json`.

| Adiabatic E_T | Krack (C1) | NLCC | NLCC − Krack | vs literature 2.840 eV | Calibration |
|---|---|---|---|---|---|
| PBE | 2.453 eV, 236.70 kJ/mol | **2.500 eV, 241.21 kJ/mol** | +0.047 eV | −0.341 eV | fails |
| PBE0 | 2.702 eV, 260.75 kJ/mol | **2.738 eV, 264.17 kJ/mol** | +0.036 eV | −0.103 eV | passes |

- PBE0 NLCC vertical absorption to T1 is 2.892 eV, vertical emission is 2.537 eV, T1 relaxation is 0.154 eV and S0 relaxation is 0.201 eV.
- The local-build controls reproduce C1's PBE/Krack energies to 1.1e-9 Ha (S0) and 6.8e-9 Ha (T1).
- **Conclusion:** the choice of pseudopotential shifts E_T by about 0.04 eV, which is small next to the functional effect (+0.25 eV). The calibration verdicts don't change.
- **Caveats:**
  - BigDFT warns that the pseudopotentials were generated with PBE but are used with PBE0.
  - With NLCC, the core charge enters only the semilocal exchange. This shifts the PBE0 total energy by 3.34 Ha compared with PBE, and the shift mostly cancels in E_T.
  - S has no NLCC file and keeps the Krack one; H switches to the Saha parametrisation.
  - No zero-point correction.
- **Fix during the run:** this Slurm node has no task plugin, so `mpirun` binding pinned concurrent jobs to the same cores. The script now uses `--bind-to none`, and jobs 808–814 were resubmitted as 815–821.
- **Cost:** PBE0 S0 took 30 min at 19.7 GB peak; PBE0 T1 took 91–92 min at 34 GB peak (8 MPI × 4 OpenMP).

## Time and tokens

| Metric | Value |
|---|---|
| Prompt sent (UTC) | 2026-10-21 08:37:06 |
| Last reply (UTC) | 2026-10-21 08:41:41 |
| Wall time | 4 min 34 s |
| API requests | 31 |
| Input tokens (uncached) | 62 |
| Cache-write input tokens | 48,395 |
| Cache-read input tokens | 3,736,023 |
| Output tokens | 19,576 |
| Total tokens | 3,804,056 |

_Source: session transcript, computed by `round_stats.py`. Does not include the compute time of background jobs._
