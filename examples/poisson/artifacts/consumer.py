"""Session B: explicitly trusted standalone continuation using only capsule files."""

import json
import sys
from pathlib import Path


def continue_study(root: Path, intervals: int = 256) -> dict:
    manifest = json.loads((root / "manifest.json").read_text())
    records = {rec["id"]: rec for rec in manifest["records"]}
    required = {
        "correct-sign",
        "wrong-sign",
        "validated-solver",
        "numerical-evidence",
        "next-grid",
    }
    if not required <= records.keys():
        raise RuntimeError("Critical research knowledge missing")
    if (
        records["correct-sign"]["supersedes"] != ["wrong-sign"]
        or records["wrong-sign"]["status"] != "superseded"
        or records["validated-solver"]["evidence"] != ["numerical-evidence"]
    ):
        raise RuntimeError("Critical correction or evidence link missing")
    evidence = json.loads((root / "results.json").read_text())
    if intervals <= max(row["intervals"] for row in evidence["validated"]):
        raise RuntimeError("Session B must use a new finer grid")
    # This import happens ONLY in the explicitly invoked trusted consumer.
    sys.path.insert(0, str(root))
    from solver import max_error

    # Reproduce session A evidence before extending it; never invent missing evidence.
    for row in evidence["validated"]:
        error = max_error(row["intervals"])
        if abs(error - row["max_error"]) > 1e-11:
            raise RuntimeError("Session A evidence could not be reproduced")
    coarse = max_error(intervals // 2)
    fine = max_error(intervals)
    ratio = coarse / fine
    if not 3.95 < ratio < 4.05 or fine >= 2e-5:
        raise RuntimeError("Second-order continuation failed")
    return {
        "session": "B",
        "intervals": intervals,
        "max_error": fine,
        "convergence_ratio": ratio,
        "critical_correction": records["correct-sign"]["content"],
        "source_memory_present": (root / "memory.json").exists(),
    }


if __name__ == "__main__":
    print(json.dumps(continue_study(Path(__file__).resolve().parent), indent=2))
