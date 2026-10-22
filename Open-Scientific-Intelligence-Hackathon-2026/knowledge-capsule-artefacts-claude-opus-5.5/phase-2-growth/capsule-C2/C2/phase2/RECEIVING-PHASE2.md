# Receiving Phase 2 (6a PBE ΔSCF on TSUBAME4.0)

This part of the capsule extends C1 with the first 6a calculations. Read the C2 `SUMMARY.md`
records tagged `6a-phase2` first; this file explains the packaged files and how to continue.

## What is packaged

| Path | Content |
|---|---|
| `phase2/inputs/NN_*.yaml` | every new BigDFT input of a stage, as YAML documents separated by `--- # <run name>`; split on that marker to recover `<run name>.yaml` files. Stage 00 = C1 `bigdft/inputs/6a_S1_*` |
| `phase2/geometries/` | plain XYZ (Å) of the PBE constrained S0/T1 minima (`cgS0`, `cgT1`) and the free S0 minimum |
| `phase2/evidence/energies.json` | per run: final energy, SCF iterations, last gnrm, magnetisation, MPI/OMP layout, geopt forces, full-log SHA-256 |
| `phase2/evidence/summary.json` | vertical/adiabatic E_T table (null = not yet computed) |
| `phase2/evidence/phase2_grid_pbe_*.json` | grid study with T1 capped at 50 iterations (superseded) and converged |
| `phase2/evidence/dryruns.json` | memory-estimation dry run of every input |
| `phase2/evidence/run_record.md` | TSUBAME job record |
| `phase2/scripts/` | job environment, array runners, restart runners, memory logger, dry-run and restart checks, task lists |
| `phase2/analysis/` | stdlib log parsers (`collect_evidence.py` produced the evidence files) |
| `tests/test_phase2_evidence.py` | stdlib regression of the evidence (run with `capsule-maker verify --trust-code`) |

Full logs are not packaged; the external artifact `phase2-results-logs-20261022` (tar.gz, SHA-256
in the manifest) holds them. Verify a local copy with
`capsule-maker verify-external C2 phase2-results-logs-20261022 FILE`.

## Run conventions (all verified on TSUBAME4.0)

- Every input is dry-run first (`scripts/dryrun_dir.sh DIR`); no calculation if any dry run fails.
- Environment: `scripts/bigdft_env.sh` (site-specific modules; `${HOME}`/`${WORK}` replace the
  original account paths). Launch with `mpirun -np N --map-by slot:PE=OMP bigdft -n NAME`.
- T1 needs `itermax: 200`, `nrepmax: 5`; the default 50 iterations do not converge.
- Restart (`inputpsiid: 2`) copies the **whole** `data-<src>` directory (incl. `glr.dat`,
  `wavefunction.yaml`) to `data-<name>`; atomic-orbital files are not needed. Restarting at a
  different geometry gives a poor guess: compute PBE wavefunctions at the target geometry first.
- PBE0 runs use full nodes (`node_f`, 24 MPI × 8 OMP) and log memory (`scripts/memwatch.sh`)
  because dry runs underestimate exact-exchange memory (C1 `fail-pbe0-oom`).
- `/work` shares the home quota on TSUBAME; wavefunction output is 6–12 GB per state.

## Next calculation

PBE0 single points at the constrained minima (stage 07: S0@cgS0, T1@cgT1, T1@cgS0, S0@cgT1),
restarting from stage 06 PBE wavefunctions, and PBE0 at S1 (stage 03). The success criterion is the
PBE0 adiabatic E_T = E(T1@cgT1) − E(S0@cgS0) within 2.79 ± 0.15 eV (C1 `dec-criteria-ok`).
Report all levels; do not tune toward 269 kJ/mol.
