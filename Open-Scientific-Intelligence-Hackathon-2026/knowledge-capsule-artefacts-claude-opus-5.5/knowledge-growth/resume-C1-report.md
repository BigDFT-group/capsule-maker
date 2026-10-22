# C1 resume report

Capsule: `C1.zip` (SHA-256 `3efb8a306f7d77513469ff4693098f5dec67a05e650b9b58962010888ed55025`), imported to `restored-C1/`.
Tooling: Capsule-Maker main @ `4a37abe` (CLI `0.1.0a1`), installed in `.venv/` from `tools/capsule-maker/`.
All capsule content was treated as untrusted data. **No bundled code was executed.**

## Transfer checks

| Step | Command | Result |
|---|---|---|
| Import | `capsule-maker import C1.zip restored-C1` | OK (schema 1.0, 63 records, 130 files, 8 sources) |
| Verify (full) | `capsule-maker verify restored-C1` | **Fails on environment only**: ase, pybigdft, pyyaml, rdkit, tblite missing from this venv |
| Verify (integrity) | `capsule-maker verify --integrity-only restored-C1` | `integrity: true`, conflicts: none, tests: not run |
| Resume | `capsule-maker resume restored-C1 > resume-C1.json` | OK |
| Review | manifest `review` | Approved by `LiiiiTx` 2026-10-20T12:50Z (a recorded decision, not proof of correctness) |
| Code-trusted tests | `verify --trust-code` | **Not run** (needs your explicit trust) |

Independent cross-check (my own arithmetic on the final `Energy (Hartree)` lines of the six packaged Phase 1 logs, no capsule code run) reproduces res-tx-pbe / res-tx-pbe0 exactly: PBE adiabatic 2.4532 eV = 236.70 kJ/mol; PBE0 adiabatic 2.7024 eV = 260.75 kJ/mol; PBE0 vertical absorption 273.64, vertical emission 238.50 kJ/mol.
A text scan of evidence, procedures and tests found no embedded instructions aimed at agents.

## Research state

**Objective** (ctx-request, ctx-target): reproduce E_T(6a) = 269 kJ/mol (2.788 eV, 77 K EtOH phosphorescence inflection) with BigDFT ΔSCF.

**Endorsed decisions (researcher, 2026-10-20)**
- dec-calibration-ok: calibrate on parent thioxanthone first.
- dec-criteria-ok: calibration passes within 0.2 eV of the literature E_T(TX); 6a is reproduced if **PBE0 adiabatic ΔSCF is 2.79 ± 0.15 eV**.
- dec-psp-ok: Krack PBE HGH-K pseudopotentials (226 e⁻ for 6a, 72 for TX).
- dec-select-ok: S1 (`bigdft/6a_S1.xyz`) is the start geometry; S3 is the sensitivity check.
- dec-dryrun-first: every input must pass a dry run before any calculation.
- dec-state: neutral closed-shell singlet, 77 atoms.

**Done**
- Phase 0: 6a structures S1/S2/S3 (res-s1/s2/s3, proc-generation); 26 + 4 BigDFT inputs, all dry-run-passed (res-dryrun, res-dryrun-pbe0).
- Phase 1, thioxanthone calibration:
  - PBE: 236.70 kJ/mol, −0.39 eV vs literature, **fails** (res-tx-calib-pbe).
  - PBE0 at PBE geometries: 260.75 kJ/mol, −0.138 eV vs literature 274.1 kJ/mol, **passes** (res-tx-calib-pbe0).
  - Literature value from a secondary source (res-tx-lit, ev-lit-tx).

**Corrections carried**
- cor-index (thioxanthone is atoms 28–42, 0-based).
- cor-strain: the S1–S3 gap is 0.453 eV, not 0.49 eV. The packaged `structures/README.md` still says 0.49 eV.
- cor-turn (type II′ torsion windows).
- hyp-pbe-underestimate → res-functional-effect (PBE0 adds +24.05 kJ/mol).

**Operational lessons that must be reused**
- fail-srun: use `mpirun`, not `srun`.
- fail-psp-api: use `set_psp_file` per element.
- fail-dryrun-env: relative `run_dir`, python on PATH, `BIGDFT_ROOT`.
- fail-pbe0-oom / res-pbe0-memory: the dry run underestimates hybrid memory. Measured on TX: about 30 GB for S0, 49–53 GB for T1.
- fail-hookean: don't use Hookean restraints.

**Open questions**
- q-pbe0-geometry, q-hybrid-psp, q-zpe, q-t1-character, q-tx-lit (primary source unverified).
- q-ensemble, q-conditions, q-complex, q-versions.
- dec-tx-grid is still *unverified*: the TX grid (h 0.35, rmult 6/9) is to be checked against the 6a convergence study.

## Next action

**Phase 2**: run the 24 dry-run-validated 6a S1 PBE single points, S0 and T1 at hgrid 0.45/0.40/0.35/0.30 × rmult (5,8)/(6,9)/(7,10), inputs in `bigdft/inputs/6a_S1_*`. Use them to choose the converged grid and check dec-tx-grid.
- Then **6a PBE0 ΔSCF** at the chosen grid.
- Size jobs from res-pbe0-memory: 6a has about 3× the electrons of thioxanthone and a larger grid.
- Compare against 2.79 ± 0.15 eV.
- Repeat on S3 for sensitivity.

**Prerequisites not met here**
- BigDFT 1.9.5 with libxc, which ctx-env says runs on a Slurm EPYC cluster.
- PyBigDFT 1.9.6.
- A compute allocation. Serial memory estimates for 6a T1 PBE reach 47.9 GB; PBE0 will be far larger.

## Requires your explicit decision
1. Trust the bundled code, so that `verify --trust-code` can run 21 stdlib tests on the structures.
2. Install the scientific environment: ase, pybigdft, pyyaml, rdkit, tblite.
3. Where to run BigDFT. The capsule's cluster scripts are site-specific; running on TSUBAME4.0 would need adapted job scripts and would spend TSUBAME points.
