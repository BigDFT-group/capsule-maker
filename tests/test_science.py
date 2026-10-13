import importlib.util
import json
import subprocess
import sys

import numpy as np
import pytest
from conftest import ROOT

from capsule_maker import CapsuleError, inspect_capsule, verify_capsule

spec = importlib.util.spec_from_file_location(
    "poisson_solver", ROOT / "examples/poisson/artifacts/solver.py"
)
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)


def test_manufactured_solution_second_order_and_discrete_residual():
    errors = [solver.max_error(n) for n in (32, 64, 128, 256)]
    assert errors[0] < 1e-3
    assert errors[-1] < 2e-5
    for coarse, fine in zip(errors, errors[1:]):
        assert 3.95 < coarse / fine < 4.05
    x, u = solver.solve_poisson(64)
    assert u[0] == u[-1] == 0
    assert (
        np.max(
            np.abs(
                (2 * u[1:-1] - u[:-2] - u[2:]) * 64**2
                - np.pi**2 * np.sin(np.pi * x[1:-1])
            )
        )
        < 1e-10
    )
    assert np.max(np.abs(-u - np.sin(np.pi * x))) > 2


def test_packaged_regressions(capsule):
    result = verify_capsule(capsule, trust_code=True)
    assert result["tests"] == "passed"
    assert "Ran 4 tests" in result["test_output"]
    assert inspect_capsule(capsule)  # disposable execution leaves inventory unchanged


def test_failed_regressions_report_failure(capsule):
    from hashlib import sha256

    data = b"import unittest\nclass Broken(unittest.TestCase):\n def test_failure(self): self.fail('broken regression')\n"
    (capsule / "tests/test_solver.py").write_bytes(data)
    value = json.loads((capsule / "manifest.json").read_text())
    item = next(i for i in value["inventory"] if i["role"] == "test")
    item.update(size=len(data), sha256=sha256(data).hexdigest())
    (capsule / "manifest.json").write_text(json.dumps(value))
    with pytest.raises(CapsuleError, match="Trusted regression tests failed"):
        verify_capsule(capsule, trust_code=True)


def test_independent_process_continuation(tmp_path):
    work = tmp_path / "handover"
    run = subprocess.run(
        [sys.executable, str(ROOT / "examples/poisson/demo.py"), "--output", str(work)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert run.returncode == 0, run.stderr
    result = json.loads(run.stdout)
    assert result["session"] == "B"
    assert result["intervals"] == 256
    assert result["max_error"] < 2e-5
    assert 3.95 < result["convergence_ratio"] < 4.05
    assert not result["source_memory_present"]
    assert result["source_memory_deleted_before_consumer"]
    assert not (work / "session-a").exists()
    assert not (work / "capsule-a").exists()
    assert (work / "session-b/continuation.json").exists()


def test_missing_evidence_consumer_fails(capsule, tmp_path):
    (capsule / "results.json").unlink()
    run = subprocess.run(
        [sys.executable, "-B", str(capsule / "consumer.py")],
        cwd=capsule,
        capture_output=True,
        text=True,
    )
    assert run.returncode != 0
    assert "FileNotFoundError" in run.stderr
