"""Generate reproducible, actually computed session-A memory and evidence."""

import importlib.util
import json
import shutil
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent / "artifacts"


def record(
    id,
    kind,
    status,
    content,
    *,
    tags=(),
    references=(),
    evidence=(),
    artifacts=(),
    supersedes=(),
    claim_key=None,
):
    result = {
        "id": id,
        "kind": kind,
        "status": status,
        "content": content,
        "tags": list(tags),
        "references": list(references),
        "evidence": list(evidence),
        "artifacts": list(artifacts),
        "provenance": ["session-a"],
        "supersedes": list(supersedes),
        "contradicts": [],
        "sensitive": False,
    }
    if claim_key:
        result["claim_key"] = claim_key
    return result


def generate(destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copytree(
        ARTIFACTS,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    spec = importlib.util.spec_from_file_location(
        "session_a_solver", ARTIFACTS / "solver.py"
    )
    solver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solver)
    import numpy as np

    x, u = solver.solve_poisson(32)
    failed_error = float(np.max(np.abs(-u - np.sin(np.pi * x))))
    results = {
        "equation": "-u'' = pi^2 sin(pi*x)",
        "boundary": [0, 0],
        "norm": "maximum absolute error",
        "units": "dimensionless",
        "failed": {
            "intervals": 32,
            "choice": "negative right-hand side",
            "max_error": failed_error,
        },
        "validated": [
            {"intervals": n, "max_error": solver.max_error(n)} for n in (32, 64, 128)
        ],
    }
    (destination / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    records = [
        record(
            "problem",
            "context",
            "unverified",
            "Solve -u''=pi^2 sin(pi*x) on [0,1] with u(0)=u(1)=0; exact u=sin(pi*x).",
            tags=["poisson"],
            references=["boundary-decision"],
        ),
        record(
            "boundary-decision",
            "decision",
            "verified",
            "Use zero Dirichlet boundaries and centered finite differences, h=1/n.",
            evidence=["numerical-evidence"],
        ),
        record(
            "wrong-sign",
            "failed_attempt",
            "superseded",
            "Using a negative right-hand side produced a negative solution with max error above 2.",
            evidence=["numerical-evidence"],
            claim_key="rhs-sign",
        ),
        record(
            "correct-sign",
            "correction",
            "verified",
            "For -u''=f use (2*u_i-u_(i-1)-u_(i+1))/h^2=f_i with a positive right-hand side.",
            supersedes=["wrong-sign"],
            evidence=["numerical-evidence"],
            claim_key="rhs-sign",
        ),
        record(
            "validated-solver",
            "procedure",
            "verified",
            "The corrected NumPy tridiagonal solver has second-order maximum-error convergence.",
            tags=["convergence", "poisson"],
            references=["problem", "correct-sign", "next-grid"],
            evidence=["numerical-evidence"],
            artifacts=[
                "solver.py",
                "tests/test_solver.py",
                "consumer.py",
                "RECEIVING.md",
            ],
        ),
        record(
            "numerical-evidence",
            "evidence",
            "verified",
            "Computed errors at 32,64,128 intervals and rejected-sign error at 32 intervals.",
            artifacts=["results.json"],
        ),
        record(
            "next-grid",
            "question",
            "unresolved",
            "Continue at 256 intervals and verify an error ratio close to four.",
            tags=["convergence"],
        ),
        record(
            "generalization",
            "hypothesis",
            "hypothesis",
            "A future extension may preserve second order for other smooth forcing functions.",
            tags=["future-forcing"],
        ),
        record(
            "unrelated",
            "context",
            "unverified",
            "Separate literature reading notes, not required for the convergence study.",
            tags=["literature"],
        ),
    ]
    roles = {
        "solver.py": "procedure",
        "tests/test_solver.py": "test",
        "consumer.py": "procedure",
        "RECEIVING.md": "instructions",
        "results.json": "evidence",
    }
    memory = {
        "format_version": "1.0",
        "origin": {
            "backend": "local-file",
            "description": "Deterministic Poisson investigation, session A",
        },
        "records": records,
        "sources": [
            {
                "id": "session-a",
                "uri": "urn:capsule-maker:poisson:session-a",
                "description": "Reproducible session_a.py calculation and curated research fixture",
            }
        ],
        "python": ">=3.11,<4",
        "artifacts": [
            {
                "path": name,
                "role": role,
                "packages": ["numpy>=1.26,<3"] if name.endswith(".py") else [],
            }
            for name, role in roles.items()
        ],
    }
    memory_path = destination / "memory.json"
    memory_path.write_text(json.dumps(memory, indent=2) + "\n")
    return memory_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    print(generate(parser.parse_args().destination))
