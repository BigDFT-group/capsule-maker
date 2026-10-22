"""Dry-run every generated input with PyBigDFT SystemCalculator(dry_run=True): bigdft-tool parses the input and
estimates memory without any SCF. Run where bigdft-tool is reachable through $BIGDFT_ROOT (the BigDFT bin dir).

    python procedures/dry_run.py INPUT_DIR WORK_DIR      # writes WORK_DIR/dryrun_summary.json
Exit status 1 if any input fails.
"""
import json
import os
import sys
from pathlib import Path

import yaml
from BigDFT.Calculators import SystemCalculator

src, work = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
rel = os.path.relpath(work)  # PyBigDFT requires run_dir to be a sub-directory of the cwd
assert not rel.startswith(".."), "WORK_DIR must be below the current directory"
work.mkdir(parents=True, exist_ok=True)
calc = SystemCalculator(omp="1", dry_run=True, verbose=False)
summary, failed = {}, []
for f in sorted(src.glob("*.yaml")):
    name = f.stem
    try:
        log = calc.run(input=yaml.safe_load(f.read_text()), name=name, run_dir=rel)
        mem = log.log.get("Estimated Memory Peak (MB)")
        grid = (log.log.get("Sizes of the simulation domain") or {}).get("Grid Spacing Units")
        summary[name] = dict(ok=mem is not None, memory_peak_MB=mem, grid=grid,
                             electrons=log.log.get("Total Number of Electrons"))
    except Exception as e:  # report and continue so every input is checked
        summary[name] = dict(ok=False, error=f"{type(e).__name__}: {e}")
    if not summary[name]["ok"]:
        failed.append(name)
    print(name, summary[name], flush=True)
(work / "dryrun_summary.json").write_text(json.dumps(summary, indent=1) + "\n")
print(f"{len(summary) - len(failed)}/{len(summary)} inputs passed the dry run")
sys.exit(1 if failed else 0)
