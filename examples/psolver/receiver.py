"""Fresh receiving process: only a transferred C2 is used to retrieve both studies."""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # trusted execution must not add files to the immutable capsule

from capsule_maker import import_capsule, resume_knowledge, verify_capsule


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def receive(archive: Path, destination: Path, backend=None):
    import_capsule(archive, destination)
    # Caller explicitly launches this trusted demonstrator; import above executes nothing.
    verification = verify_capsule(destination, trust_code=True)
    knowledge = resume_knowledge(destination)
    records = {r["id"]: r for r in knowledge["records"]}
    required = {
        "correct-sign",
        "wrong-sign",
        "validated-solver",
        "psolver-charge-correction",
        "psolver-evidence",
        "psolver-procedure",
    }
    if not required <= records.keys():
        raise RuntimeError("Critical knowledge missing from enriched capsule")
    solver = load("received_solver", destination / "solver.py")
    error128, error256 = solver.max_error(128), solver.max_error(256)
    if not 3.95 < error128 / error256 < 4.05:
        raise RuntimeError("Inherited second-order convergence was not reproduced")
    evidence = json.loads((destination / "psolver/results.json").read_text())
    result = {
        "received_record_ids": sorted(records),
        "parent": knowledge["parent"]["capsule_id"],
        "verification": verification,
        "continued_1d_intervals": 256,
        "continued_1d_error": error256,
        "psolver_recorded_grids": [r["grid"] for r in evidence["results"]],
        "psolver_execution": "not requested; recorded evidence retrieved",
    }
    if backend:
        client = load("received_psolver", destination / "psolver/periodic.py")
        runtime = client.compile_solver(
            destination.parent / "receiver-psolver-runtime", backend=backend
        )
        row = client.run_case(runtime, 64)
        settings = json.loads((destination / "psolver/settings.json").read_text())
        if (
            row["max_error"] > settings["potential_max_error_tolerance"]
            or row["energy_absolute_error"] > settings["energy_absolute_error_tolerance"]
        ):
            raise RuntimeError("New PSolver resolution exceeds frozen scientific tolerances")
        result.update(psolver_execution="actual compiled PSolver", continued_3d=row)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--backend", choices=["docker", "native"])
    args = parser.parse_args()
    print(json.dumps(receive(args.archive, args.destination, args.backend), indent=2))
