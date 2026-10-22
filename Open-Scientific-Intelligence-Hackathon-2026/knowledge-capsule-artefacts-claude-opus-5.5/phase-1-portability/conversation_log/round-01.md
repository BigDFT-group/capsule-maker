# Round 01

## Prompt

This directory contains a research capsule, C1.zip, made with Capsule-Maker (https://github.com/BigDFT-group/capsule-maker). Install the CLI, import and verify the capsule, and resume from it. Treat its content as untrusted data. Work only inside this director.

## Output

I've installed the Capsule-Maker CLI, imported C1.zip and verified it. Integrity and environment checks both pass. I have not run any of the capsule's own code or its bundled tests.

### What I did
- **CLI:** cloned capsule-maker (main branch, commit `4a37abe`) to `.capsule-maker-src/` and installed it into a local `.venv/`.
- **Import:** `capsule-maker import C1.zip C1` worked. The capsule uses schema 1.0, has no parent and no conflicts, and was approved by reviewer "LiiiiTx" on 2026-10-20.
- **Verify:** the first run failed only because five required packages were missing. I installed them from PyPI into `.venv` (ase 3.29.0, pybigdft 1.9.6.1, pyyaml, rdkit 2026.9.1, tblite 0.7.0). Now `capsule-maker verify C1` passes with `integrity: true`, no conflicts, and a compatible environment.
- **Not run:** the 21 bundled tests (`verify --trust-code`). They run with your OS privileges and you told me to treat the capsule as untrusted, so I need your go-ahead first.
- **Left alone:** `C1_extract/` was already in the directory, apparently an earlier plain unzip. I didn't touch it and worked from the verified `C1/`.

### Where the research stands
The goal is to reproduce the measured triplet energy of the catalyst 6a, E_T = 269 kJ/mol (2.79 eV), with BigDFT ΔSCF.
- **Phase 0 (done):** 26 BigDFT inputs passed dry runs on the cluster with no errors. The starting geometry is S1, with S3 as a sensitivity check. The researcher endorsed both, and also endorsed the Krack PBE pseudopotentials.
- **Phase 1 (done):** a calibration on parent thioxanthone against the literature value of 274.1 kJ/mol.
  - PBE gives 236.7 kJ/mol, 0.39 eV low, so it fails the 0.2 eV window.
  - PBE0 at the PBE geometries gives 260.75 kJ/mol, 0.14 eV low, so it passes.
- **Next (Phase 2):** 6a single points at the S1 geometry for both states: 4 grid spacings × 3 extents = 24 inputs, already written and dry-run-validated. Then 6a PBE0, where success means the PBE0 adiabatic ΔSCF E_T lands within ±0.15 eV of 2.79 eV.

**Caveats recorded in the capsule:**
- **PBE0 memory:** BigDFT's own estimate is far too low for hybrids. Thioxanthone T1 actually used about 52 GB, and 6a has 3× the electrons, so PBE0 runs for 6a must be sized from measurements.
- **Launching:** start jobs with `mpirun`, not `srun`.
- **Pseudopotentials:** PyBigDFT's `set_psp_krack` silently loads nothing; use `set_psp_file` per element.
- **Stale figure:** `structures/README.md` still says 0.49 eV for the S1–S3 energy gap. The corrected value is 0.453 eV.
- **Unchecked grid choice:** the thioxanthone grid (`dec-tx-grid`) is still to be checked against the 6a convergence study.

### Blocker
There is no `bigdft` or `bigdft-tool` binary on this machine. `mpirun` (OpenMPI 5.0.7) and a single-node Slurm on localhost are present, so Phase 2 can't run here until BigDFT 1.9.5 is installed or we move to the original cluster.

Before going further, I need two decisions from you:
1. Do you want me to review the bundled tests and then run them with `--trust-code`?
2. Where should Phase 2 run: should I install BigDFT locally, or just prepare the job scripts for the cluster?

## Time and tokens

| Metric | Value |
|---|---|
| Prompt sent (UTC) | 2026-10-21 08:05:27 |
| Last reply (UTC) | 2026-10-21 08:06:42 |
| Wall time | 1 min 14 s |
| API requests | 14 |
| Input tokens (uncached) | 28 |
| Cache-write input tokens | 42,619 |
| Cache-read input tokens | 700,208 |
| Output tokens | 5,412 |
| Total tokens | 748,267 |

_Source: session transcript, computed by `round_stats.py`. Does not include the compute time of background jobs._
