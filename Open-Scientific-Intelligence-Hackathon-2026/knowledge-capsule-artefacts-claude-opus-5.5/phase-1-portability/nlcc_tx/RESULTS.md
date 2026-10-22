# Thioxanthone triplet energy with NLCC pseudopotentials

Repeats the C1 Phase 1/1b ΔSCF triplet calculation for thioxanthone, changing only the pseudopotentials. Computed 2026-10-21.

## Setup
- **Geometries:** C1's converged PBE S0 and T1 structures (`C1/bigdft/runs/tx_{S0,T1}_pbe_geopt/final_*.yaml`), with no re-optimisation.
- **Settings:** the same as C1: hgrid 0.35 bohr, rmult (6, 9), gnrm_cv 1e-5, free boundary conditions, T1 as nspin 2 / mpol 2.
- **Pseudopotentials:** the C1 Krack PBE psppar is loaded first for every element (C, H, O, S). The PyBigDFT NLCC set (`Database/psppar/SS`, Saha 2015, XC −101130 = PBE) is then loaded on top for every element it provides.
  - C and O: HGH-K + NLCC.
  - H: HGH-K, from the Saha 2015 set (no core correction).
  - S: no NLCC file exists, so it keeps the C1 Krack file.
  - Electron count: 72, the same as C1.
- **Code:** BigDFT 1.9.5 (local build `~/Softwares/bigdft`, 1.9.5.221), PyBigDFT 1.9.6.1, OpenMPI 5.0.7, 8 MPI × 4 OpenMP per job on local Slurm.
- **Checks before running:** all 10 inputs passed the dry run before any calculation. Grid 101×75×62, the same as C1.
- **Control:** C1's PBE/Krack S0 and T1 energies were recomputed with this build. They differ from C1 by 1.1e-9 and 6.8e-9 Ha.

## Energies (Ha), all converged
| State @ geometry | PBE, NLCC | PBE0, NLCC |
|---|---|---|
| S0 @ S0 | −116.849975511 | −113.510154505 |
| S0 @ T1 | −116.844579247 | −113.502760998 |
| T1 @ S0 | −116.752991503 | −113.403865914 |
| T1 @ T1 | −116.758103383 | −113.409538876 |

Both T1 states have magnetisation 2.000. NLCC shifts the total energies, so only differences between states are comparable with C1.

## Triplet energies compared with C1 (Krack PBE pseudopotentials)
| Quantity | PBE Krack (C1) | PBE NLCC | PBE0 Krack (C1) | PBE0 NLCC |
|---|---|---|---|---|
| **Adiabatic E_T** | 236.70 kJ/mol, 2.453 eV | **241.21 kJ/mol, 2.500 eV** | 260.75 kJ/mol, 2.702 eV | **264.17 kJ/mol, 2.738 eV** |
| NLCC − Krack | | +4.51 kJ/mol, +0.047 eV | | +3.42 kJ/mol, +0.036 eV |
| Difference from literature (274.1 kJ/mol, 2.840 eV) | −0.388 eV | −0.341 eV | −0.138 eV | **−0.103 eV** |
| Calibration (within 0.2 eV) | fails | **fails** | passes | **passes** |
| Difference from 6a experiment (269 kJ/mol) | −32.3 kJ/mol | −27.8 kJ/mol | −8.25 kJ/mol | −4.83 kJ/mol |
| Vertical absorption to T1 (at S0) | — | 254.63 kJ/mol, 2.639 eV | 273.64 kJ/mol, 2.836 eV | 279.06 kJ/mol, 2.892 eV |
| Vertical emission (at T1) | — | 227.04 kJ/mol, 2.353 eV | 238.50 kJ/mol, 2.472 eV | 244.75 kJ/mol, 2.537 eV |
| T1 relaxation | — | 0.139 eV | 0.134 eV | 0.154 eV |
| S0 relaxation | — | 0.147 eV | 0.231 eV | 0.201 eV |

## Conclusions
- **Small effect:** switching to NLCC pseudopotentials raises the adiabatic triplet energy by only 0.036–0.047 eV. That is small next to the functional effect (PBE → PBE0 is +0.24 to +0.25 eV).
- **Calibration verdicts unchanged:** PBE still fails and PBE0 still passes. PBE0 with NLCC lands 0.10 eV below the literature value, against 0.14 eV with Krack.
- **Pseudopotential sensitivity:** the difference between the two pseudopotential families, about 0.04 eV, is an estimate of how much the C1 protocol depends on pseudopotential choice.

## Caveats
- **PBE pseudopotentials with PBE0:** BigDFT warns "PSP generated with a different XC", as it did in C1.
- **NLCC with a hybrid functional:** the core charge enters only the semilocal part of the exchange–correlation energy. Exact exchange uses valence electrons only, so PBE0 drops 25% of the core–valence exchange. This shifts the PBE0 total energy by 3.34 Ha relative to PBE, against 0.04 Ha with Krack. The shift mostly cancels between S0 and T1, but it is a methodological inconsistency.
- **Mixed pseudopotential set:** S, the heavy atom next to the chromophore, has no core correction. H also changes parametrisation, from the Krack H to the Saha H, not only C and O.
- **Not included:** zero-point energy, solvent and PBE0 geometries, as in C1.
- **Different build:** the jobs ran on a local BigDFT build, not the cluster module used for C1. The controls agree with C1 to below 1e-8 Ha.

## Cost (8 MPI × 4 OpenMP, two jobs sharing 32 cores)
- **PBE:** 1–3 min per point.
- **PBE0 S0:** 30 min, 19.7 GB peak.
- **PBE0 T1:** 91–92 min, 34 GB peak.

## Files
- `make_nlcc_inputs.py`: input generator.
- `inputs/`: the inputs, plus `index.json` listing the pseudopotential source for each element.
- `dry_run.py` and `dryrun/`: the dry-run script and its output.
- `run_bigdft.slurm`: the job script.
- `runs/`: the BigDFT runs.
- `analyze_nlcc.py`: the analysis script; its output is `nlcc_summary.json`.
