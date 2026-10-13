"""Portable evidence tests always run; compiled-library validation is explicitly opt-in."""

import importlib.util
import json
import os
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

import numpy as np
import pytest

from capsule_maker import (
    Goal,
    LocalFileAdapter,
    approve_capsule,
    compare_capsules,
    export_capsule,
    extend_capsule,
    import_capsule,
    inspect_capsule,
    verify_capsule,
)

EXAMPLE = Path(__file__).resolve().parents[1] / "examples/psolver"
spec = importlib.util.spec_from_file_location("psolver_session_b", EXAMPLE / "session_b.py")
session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session)


def test_periodic_charge_and_calibration():
    client = session.load_client()
    rho, exact = client.prepare_charge(32)
    x = 2 * np.pi * np.arange(32) / 32
    # Analytical continuous eigenmode has -laplacian V=3V; Coulomb RHS=4*pi*rho.
    expected = np.sin(x)[:, None, None] * np.sin(x)[None, :, None] * np.sin(x)[None, None, :]
    np.testing.assert_allclose(exact, expected, rtol=0, atol=0)
    np.testing.assert_allclose(rho * 4 * np.pi, 3 * expected, rtol=3e-16, atol=1e-16)
    for n in (8, 17, -16, True):
        with pytest.raises(ValueError):
            client.prepare_charge(n)
    measured = json.loads((EXAMPLE / "calibration.json").read_text())
    session.validate(measured)
    assert (
        sha256((EXAMPLE / "artifacts/psolver_periodic.f90").read_bytes()).hexdigest()
        == measured["runtime"]["driver_source_sha256"]
    )


def test_evidence_criteria_do_not_substitute_missing_results():
    measured = json.loads((EXAMPLE / "calibration.json").read_text())
    measured["results"].pop()
    with pytest.raises(ValueError):
        session.validate(measured)
    measured = json.loads((EXAMPLE / "calibration.json").read_text())
    measured["results"][0]["max_error"] = 1e-3
    with pytest.raises(ValueError):
        session.validate(measured)


def test_recorded_psolver_capsule_independent_of_compiled_library(capsule, tmp_path):
    approve_capsule(capsule, "fixture-review")
    measured = json.loads((EXAMPLE / "calibration.json").read_text())
    memory = session.curate(tmp_path / "psolver-memory", measured)
    child = tmp_path / "C2"
    extended = extend_capsule(
        capsule, LocalFileAdapter(memory), Goal("Periodic", ("psolver",)), child
    )
    assert {"psolver-charge-correction", "correct-sign"} <= {r["id"] for r in extended["records"]}
    assert compare_capsules(capsule, child)["direct_child"]
    approve_capsule(child, "fixture-review")
    archive = export_capsule(child, tmp_path / "C2.zip")
    import_capsule(archive, tmp_path / "independent")
    assert verify_capsule(tmp_path / "independent", trust_code=True)["tests"] == "passed"
    receiver = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(EXAMPLE / "receiver.py"),
            str(archive),
            str(tmp_path / "fresh"),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert receiver.returncode == 0, receiver.stderr
    result = json.loads(receiver.stdout)
    assert result["continued_1d_intervals"] == 256
    assert result["psolver_recorded_grids"] == [[n] * 3 for n in (16, 24, 32, 48)]
    assert result["psolver_execution"].startswith("not requested")
    assert inspect_capsule(tmp_path / "fresh") == inspect_capsule(child)


@pytest.mark.psolver
@pytest.mark.skipif(
    os.environ.get("CAPSULE_PSOLVER_BACKEND") not in {"docker", "native"},
    reason="Set CAPSULE_PSOLVER_BACKEND=docker/native to explicitly run installed PSolver",
)
def test_actual_psolver_evolution_and_new_grid(tmp_path):
    # Full actual scientific study and independent 64^3 continuation, no substituted solver.
    run = subprocess.run(
        [
            sys.executable,
            str(EXAMPLE / "demo.py"),
            "--output",
            str(tmp_path / "demo"),
            "--backend",
            os.environ["CAPSULE_PSOLVER_BACKEND"],
        ],
        text=True,
        capture_output=True,
        check=False,
        timeout=240,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    report = json.loads(run.stdout)
    assert report["parent_unchanged"] and report["source_memories_deleted"]
    assert report["independent_continuation"]["continued_3d"]["grid"] == [64] * 3
    assert report["sizes"]["C2"]["directory_bytes"] < 100_000
    assert report["sizes"]["raw_audit_zip_bytes"] > 10 * report["sizes"]["C2_zip_bytes"]
    session.validate(report["psolver_results"])


def test_scientific_checks_survive_python_optimization(tmp_path):
    measured = json.loads((EXAMPLE / "calibration.json").read_text())
    measured["results"][0]["max_error"] = 1e-3
    evidence = tmp_path / "bad-results.json"
    evidence.write_text(json.dumps(measured))
    code = (
        "import importlib.util,json; "
        "s=importlib.util.spec_from_file_location('validation', __import__('sys').argv[1]); "
        "v=importlib.util.module_from_spec(s); s.loader.exec_module(v); "
        "v.validate_results(json.load(open(__import__('sys').argv[2])), "
        "json.load(open(__import__('sys').argv[3])))"
    )
    run = subprocess.run(
        [
            sys.executable,
            "-I",
            "-O",
            "-c",
            code,
            str(EXAMPLE / "artifacts/validation.py"),
            str(evidence),
            str(EXAMPLE / "artifacts/settings.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode != 0 and "Scientific validation failed" in run.stderr
