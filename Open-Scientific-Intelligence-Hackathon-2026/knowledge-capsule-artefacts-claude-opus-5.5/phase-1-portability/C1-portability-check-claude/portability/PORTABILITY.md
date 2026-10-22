# Portability check of C1 (Claude Opus 5.5, 2026-10-21)

This report covers taking capsule C1 to a new machine. A fresh agent session with no access to the original conversation or memory imported it, verified it, resumed from it, and extended it.

## Steps and outcome
| Step | Outcome |
|---|---|
| Install Capsule-Maker | Main branch `4a37abe` installed in a Python 3.12.9 venv with `[science]` extras |
| `import C1.zip C1` | Succeeded: integrity true, schema 1.0, no conflicts, review by LiiiiTx dated 2026-10-20 |
| `verify C1` | First run failed only on the environment (ase, pybigdft, pyyaml, rdkit, tblite missing). Passed after installing them from PyPI |
| `verify --trust-code` | Not run, because the researcher did not authorise running the capsule's code |
| `resume C1` | Returned all 63 records, 0 conflicts |
| Use the C1 knowledge | Enough to rebuild the thioxanthone protocol without the original session: the pseudopotential workaround, the dry-run rule, `mpirun` instead of `srun`, PBE0 memory sizing, and the run-directory rule |
| Reproduce C1 numbers | Running the C1 Krack inputs at the C1 PBE minima on a different BigDFT build and CPU gives S0 and T1 energies within 1.1e-9 and 6.8e-9 Ha |
| Extend C1 | NLCC pseudopotential study of the thioxanthone triplet energy (see `nlcc/RESULTS.md`) |

## Problems the capsule did not anticipate
1. **Missing BigDFT module.** The receiving machine has no `bigdft/rho0` module, and C1's Slurm script loads it. A local 1.9.5 build in `~/Softwares/bigdft` was used instead.
2. **PyBigDFT run-directory rule.** PyBigDFT rejects any `run_dir` that contains `/`. C1 recorded only that absolute paths are rejected, so C1's `dry_run.py` must be run from inside the work directory.
3. **Strict mode and `bigdftvars.sh`.** `bigdftvars.sh` uses unset variables, so the Slurm script must source it before `set -u`.
4. **CPU pinning on a single-node Slurm.** This node has no task plugin, so explicit `mpirun` binding pins concurrent jobs to the same cores. Use `--bind-to none`.
5. **Misleading log comment.** The local build prints "#DoLastRunThings triggered without convergence" on every final SCF cycle. Read convergence from the `#FINAL` iteration and its gnrm instead.

## Knowledge checks
- **Confirmed again:** `set_psp_nlcc(elements=[...])` loads nothing in PyBigDFT 1.9.6.1 (C1's `fail-psp-api`). The bigdft-skills plugin's `pseudopotentials` skill still recommends that form.
- **Stale value:** C1's `structures/README.md` still gives 0.49 eV for the S1–S3 energy gap. C1's own correction record says 0.453 eV, and that record was the one followed.

## Not done
- The 6a calculations (Phase 2 onward).
- C1's bundled tests.
- Any PBE0 geometry optimisation.
