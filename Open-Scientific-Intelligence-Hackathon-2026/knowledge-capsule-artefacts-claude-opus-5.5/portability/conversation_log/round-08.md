# Round 08

## Prompt

make a new capsule C1-portability-check-claude.

## Output

I've created `C1-portability-check-claude/` as a child of C1 with `capsule-maker extend`. It has every C1 record plus 18 new records covering this session. It isn't approved or exported yet, because recording the review is up to you.

### What's in it
- **Format:** schema 1.1 with parent lineage. C1's manifest and summary are embedded under `lineage/`.
- **Size:** 81 records (63 inherited, 18 new), 173 files, 6.9 MB.
- **C1 unchanged:** C1's own integrity check still passes. In the comparison every inherited record is unchanged, nothing is removed, and the 18 new records are added.
- **Tags:** `portability` and `nlcc-tx`.

The 18 new records, by kind:
- **Request and evidence:**
  - `pc-request`: your instructions, including the NLCC procedure.
  - `pc-requests`: the question sheet, packaged as evidence.
  - `pc-evidence`: all the packaged files.
- **Portability:**
  - `pc-import`: import and verify outcome, and the dependencies that had to be installed.
  - `pc-env`: the receiving machine.
  - `pc-control`: the local build reproduces C1's PBE energies to within 1e-8 Ha.
  - `pc-cost`: runtimes and memory.
- **The NLCC study:**
  - `pc-psp-procedure`: decision recording your pseudopotential procedure.
  - `pc-procedure`: the scripts that make the inputs, run the jobs and analyse the results.
  - `pc-dryrun`: all 10 inputs passed the dry run.
  - `pc-tx-nlcc-pbe`: E_T = 2.500 eV with PBE.
  - `pc-tx-nlcc-pbe0`: E_T = 2.738 eV with PBE0 (passes the calibration).
  - `pc-psp-sensitivity`: switching from Krack to NLCC changes E_T by about 0.04 eV, and neither calibration verdict changes.
- **Open question:** `pc-nlcc-hybrid` notes that NLCC is inconsistent with PBE0 (the 3.34 Ha shift in total energy).
- **Lessons learned:**
  - `pc-fail-binding`: CPU pinning on a single-node Slurm.
  - `pc-fail-rundir`: PyBigDFT rejects any `run_dir` containing `/`, and `bigdftvars.sh` breaks under `set -u`.
  - `pc-psp-api-confirmed`: the `set_psp_nlcc` bug is still present, and the BigDFT plugin skill's example uses the broken form.
  - `pc-log-comment`: a misleading BigDFT log comment about convergence.

### What I packaged and what I left out
- **Added files:**
  - `nlcc/procedures/`: 3 scripts.
  - `nlcc/inputs/`: 10 inputs plus `index.json`.
  - The dry-run summary.
  - The BigDFT log and Slurm output for each of the 10 runs.
  - `nlcc/nlcc_summary.json` and `nlcc/RESULTS.md`.
  - `portability/PORTABILITY.md` and `portability/QUESTIONS.md`.
  - `tests/test_nlcc.py`: 7 checks using only the Python standard library.
- **Left out:** Capsule-Maker allows at most 200 files per capsule and C1 already has 131. The forces and timing files, the input copies inside `runs/`, and the dry-run logs stay in the local `nlcc_tx/`. The evidence record says so.
- **Redacted paths:** as C1 did, the local BigDFT install path and home directory are replaced with placeholders. Nothing under `/home/` remains in the new files.

### Checks
- `capsule-maker verify`: integrity true, no conflicts, lineage verified, environment compatible.
- `verify-parent` against the local C1 copy: matches.
- `tests/test_nlcc.py` (7 tests): pass. They check convergence, that the energies in the summary match the logs, the control against C1's numbers, the E_T values, the calibration verdicts, which pseudopotential each element got, and that the geometries equal C1's PBE minima.
- I did not run the full `verify --trust-code`, because it would also run C1's tests, which you haven't authorised.

### Build files
- `capsule_build/build_memory.py`: the curation script.
- `capsule_build/memory/`: the memory it assembles from `nlcc_tx/`.
- `capsule_build/PORTABILITY.md`: the report.
- `capsule_build/tests/test_nlcc.py`: the test file.

### Next steps (yours)
Review the capsule, record your approval, then export it:
```bash
.venv/bin/capsule-maker contents C1-portability-check-claude --path SUMMARY.md
.venv/bin/capsule-maker approve C1-portability-check-claude --reviewer "YOUR_ID"
.venv/bin/capsule-maker export C1-portability-check-claude C1-portability-check-claude.zip
```

## Time and tokens

| Metric | Value |
|---|---|
| Prompt sent (UTC) | 2026-10-21 11:16:44 |
| Last reply (UTC) | 2026-10-21 11:20:52 |
| Wall time | 4 min 07 s |
| API requests | 21 |
| Input tokens (uncached) | 42 |
| Cache-write input tokens | 41,912 |
| Cache-read input tokens | 4,762,014 |
| Output tokens | 24,955 |
| Total tokens | 4,828,923 |

_Source: session transcript, computed by `round_stats.py`. Does not include the compute time of background jobs._
