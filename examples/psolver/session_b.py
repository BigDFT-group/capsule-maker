"""Curate real PSolver measurements as new local records, not agent-memory consolidation."""

import importlib.util
import json
import shutil
import zipfile
from hashlib import sha256
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent / "artifacts"


def load_client():
    spec = importlib.util.spec_from_file_location("psolver_client", ARTIFACTS / "periodic.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(results):
    spec = importlib.util.spec_from_file_location("psolver_validation", ARTIFACTS / "validation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.validate_results(results, json.loads((ARTIFACTS / "settings.json").read_text()))


def curate(destination: Path, results: dict, external=None) -> Path:
    """Write inspected evidence. Callers must identify how supplied results were obtained."""
    validate(results)  # Missing evidence or criteria failures must stop capsule generation.
    destination.mkdir(parents=True, exist_ok=False)
    solver = destination / "psolver"
    solver.mkdir()
    for name in (
        "periodic.py",
        "psolver_periodic.f90",
        "validation.py",
        "settings.json",
        "RECEIVING-PSOLVER.md",
    ):
        shutil.copyfile(ARTIFACTS / name, solver / name)
    (destination / "tests").mkdir()
    shutil.copyfile(
        ARTIFACTS / "tests/test_psolver_evidence.py", destination / "tests/test_psolver_evidence.py"
    )
    (solver / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    records = []

    def record(
        identifier,
        kind,
        status,
        content,
        *,
        references=(),
        evidence=(),
        artifacts=(),
        supersedes=(),
    ):
        item = {
            "id": identifier,
            "kind": kind,
            "status": status,
            "content": content,
            "tags": ["psolver"],
            "references": list(references),
            "evidence": list(evidence),
            "artifacts": list(artifacts),
            "provenance": ["psolver-session-b"],
            "supersedes": list(supersedes),
            "contradicts": [],
            "sensitive": False,
        }
        records.append(item)
        return item

    record(
        "psolver-objective",
        "context",
        "unverified",
        "Extend the 1D investigation to a 3D periodic cube [0,2*pi)^3 in atomic units, with V=sin(x)*sin(y)*sin(z).",
        references=["validated-solver", "correct-sign", "psolver-procedure", "psolver-next-grid"],
    )
    record(
        "psolver-wrong-normalization",
        "failed_attempt",
        "superseded",
        "Treating mathematical -laplacian(V)=rho as PSolver's convention caused potential error 11.56637 at 16^3.",
        evidence=["psolver-evidence"],
    )
    record(
        "psolver-charge-correction",
        "correction",
        "verified",
        "PSolver solves -laplacian(V)=4*pi*rho; prepare rho=3*V/(4*pi). The wrong convention is rejected, not silently overwritten.",
        supersedes=["psolver-wrong-normalization"],
        evidence=["psolver-evidence"],
    )
    record(
        "psolver-grid-rejection",
        "failed_attempt",
        "unverified",
        "Exploratory 8^3 grid was rejected: box too small for ISF16. Fortran STOP returned zero but produced no potential; client checks output existence. Use n>=16, divisible by eight.",
    )
    record(
        "psolver-gauge-and-api",
        "decision",
        "verified",
        "Use neutral density, periodic boundaries, zero-mean potential; H_potential overwrites rhopot, not pot_ion. Compare the zero-mean output; analytical Hartree energy is 3*pi^2/8.",
        evidence=["psolver-evidence"],
    )
    record(
        "psolver-procedure",
        "procedure",
        "verified",
        f"Standalone PSolver {results['runtime']['psolver_version']} ISF16 CPU, one MPI rank and one OpenMP thread, meets fixed potential/energy bounds at 16,24,32,48 cubed. This is not the 1D second-order stencil: errors reach roundoff after refinement.",
        references=["psolver-charge-correction", "psolver-gauge-and-api", "psolver-grid-rejection"],
        evidence=["psolver-evidence"],
        artifacts=[
            "psolver/periodic.py",
            "psolver/psolver_periodic.f90",
            "psolver/validation.py",
            "psolver/settings.json",
            "psolver/RECEIVING-PSOLVER.md",
            "tests/test_psolver_evidence.py",
        ],
    )
    evidence = record(
        "psolver-evidence",
        "evidence",
        "verified",
        "Actual compiled-library four-grid results and failed-normalization control, including library, driver, compiler and image fingerprints. Portable tests check evidence and charge; optional integration reruns PSolver.",
        artifacts=["psolver/results.json"],
    )
    if external:
        evidence["external_artifacts"] = [external["id"]]
    record(
        "psolver-next-grid",
        "question",
        "unresolved",
        "Continue at 64^3; assess potential and Hartree energy within versioned absolute bounds. Do not infer a convergence order from roundoff-level errors.",
    )
    roles = {
        "psolver/periodic.py": "procedure",
        "psolver/psolver_periodic.f90": "procedure",
        "psolver/validation.py": "procedure",
        "psolver/settings.json": "data",
        "psolver/results.json": "evidence",
        "psolver/RECEIVING-PSOLVER.md": "instructions",
        "tests/test_psolver_evidence.py": "test",
    }
    memory = {
        "format_version": "1.1",
        "origin": {
            "backend": "local-file",
            "description": "Standalone PSolver periodic investigation, session B",
        },
        "records": records,
        "sources": [
            {
                "id": "psolver-session-b",
                "uri": "urn:capsule-maker:psolver:session-b",
                "description": "Actual PSolver computation with compact numerical evidence and checksummed runtime provenance",
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
        "external_artifacts": [external] if external else [],
    }
    path = destination / "memory.json"
    path.write_text(json.dumps(memory, indent=2) + "\n")
    return path


def investigate(destination: Path, raw_work: Path, archive: Path, *, backend: str):
    results = load_client().investigate(raw_work, backend=backend)
    validate(results)
    # Raw logs and arrays only; do not redistribute compiled GPL libraries or environments.
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as stream:
        for path in sorted(raw_work.rglob("*")):
            if path.is_file() and (path.name.endswith(".txt") or path.name.endswith(".log")):
                stream.write(path, path.relative_to(raw_work).as_posix())
        stream.writestr("results.json", json.dumps(results, indent=2))
        stream.writestr("settings.json", (ARTIFACTS / "settings.json").read_text())
    fingerprint = sha256(archive.read_bytes()).hexdigest()
    external = {
        "id": "psolver-raw-audit",
        "uri": "urn:sha256:" + fingerprint,
        "sha256": fingerprint,
        "size": archive.stat().st_size,
        "description": "Optional raw charge/potential arrays, logs and settings; locate by checksum, no automatic fetching",
        "dependencies": [
            "PSolver==" + results["runtime"]["psolver_version"],
            results["runtime"]["compiler"],
            results["runtime"]["image"] or "native GNU/OpenMPI",
        ],
        "required_for_reproduction": False,
    }
    return curate(destination, results, external), results
