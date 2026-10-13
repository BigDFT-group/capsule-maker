"""Explicitly invoked client for the actual installed BigDFT PSolver library."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from hashlib import sha256
from pathlib import Path

import numpy as np

PINNED_IMAGE = (
    "bigdft/core-sdk@sha256:669262a09473586c8b0ed6dd877a19b7791c5b81ad79b84affbe9def5e5aa352"
)


def prepare_charge(n: int):
    if isinstance(n, bool) or not isinstance(n, int) or n < 16 or n % 8:
        raise ValueError(
            "Periodic grid size must be an integer multiple of 8, at least 16 for ISF order 16"
        )
    x = 2 * np.pi * np.arange(n) / n
    potential = np.sin(x)[:, None, None] * np.sin(x)[None, :, None] * np.sin(x)[None, None, :]
    density = 3 * potential / (4 * np.pi)
    return density, potential


def _run(command, cwd=None, timeout=120):
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    env["OMP_NUM_THREADS"] = "1"
    result = subprocess.run(
        command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout, check=False
    )
    if result.returncode:
        raise RuntimeError("PSolver command failed:\n" + result.stdout + result.stderr)
    return result


def compile_solver(work: Path, *, backend: str, image: str = PINNED_IMAGE) -> dict:
    """Compile this original client against the separately installed public API.

    This is scientific execution, never called by Capsule-Maker import/inspection.
    No fallback numerical solver is provided. Docker uses an existing image only.
    """
    work.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).with_name("psolver_periodic.f90")
    shutil.copyfile(source, work / "psolver_periodic.f90")
    script = (
        "set -eu\n"
        "pkg-config --modversion psolver > library-version.txt\n"
        "gfortran --version | head -1 > compiler-version.txt\n"
        "mpif90 --showme:version > mpi-version.txt\n"
        'sha256sum "$(pkg-config --variable=libdir psolver)/libPSolver-1.a" > library-sha256.txt\n'
        'mpif90 -O2 -fopenmp -I"$(pkg-config --variable=includedir psolver)" '
        "psolver_periodic.f90 -o psolver_periodic $(pkg-config --cflags --libs psolver)\n"
    )
    if backend == "docker":
        if not shutil.which("docker"):
            raise RuntimeError("Docker is unavailable; install a documented PSolver environment")
        _run(["docker", "image", "inspect", image])
        _run(
            [
                "docker",
                "run",
                "--rm",
                "--pull=never",
                "--network",
                "none",
                "-e",
                "OMP_NUM_THREADS=1",
                "--mount",
                f"type=bind,source={work.resolve()},target=/work",
                "--workdir",
                "/work",
                image,
                "bash",
                "-c",
                script,
            ]
        )
    elif backend == "native":
        if not shutil.which("mpif90") or not shutil.which("pkg-config"):
            raise RuntimeError(
                "Native PSolver requires mpif90 and pkg-config with psolver installed"
            )
        _run(["bash", "-c", script], cwd=work)
    else:
        raise ValueError("Choose backend='docker' or backend='native'")
    return {
        "backend": backend,
        "image": image if backend == "docker" else None,
        "psolver_version": (work / "library-version.txt").read_text().strip(),
        "compiler": (work / "compiler-version.txt").read_text().strip(),
        "mpi": (work / "mpi-version.txt").read_text().strip(),
        "library_sha256": (work / "library-sha256.txt").read_text().split()[0],
        "driver_source_sha256": sha256(source.read_bytes()).hexdigest(),
        "executable_sha256": sha256((work / "psolver_periodic").read_bytes()).hexdigest(),
        "work": str(work.resolve()),
    }


def run_case(runtime: dict, n: int, *, normalization: str = "coulomb") -> dict:
    work = Path(runtime["work"])
    label = f"n{n}-{normalization}"
    case = work / label
    case.mkdir(exist_ok=False)
    density, reference = prepare_charge(n)
    if normalization == "mathematical":
        density = density * (4 * np.pi)  # deliberate rejected interpretation -laplace V = rho
    elif normalization != "coulomb":
        raise ValueError("Unknown charge convention")
    np.savetxt(case / "density.txt", density.ravel(order="F"), fmt="%.17e")
    args = [str(n), f"{label}/density.txt", f"{label}/potential.txt", f"{label}/energy.txt"]
    if runtime["backend"] == "docker":
        command = [
            "docker",
            "run",
            "--rm",
            "--pull=never",
            "--network",
            "none",
            "-e",
            "OMP_NUM_THREADS=1",
            "--mount",
            f"type=bind,source={work},target=/work",
            "--workdir",
            "/work",
            runtime["image"],
            "./psolver_periodic",
            *args,
        ]
    else:
        command = [str(work / "psolver_periodic"), *args]
    run = _run(command, cwd=work)
    (case / "stdout.log").write_text(run.stdout)
    (case / "stderr.log").write_text(run.stderr)
    if not (case / "potential.txt").is_file() or not (case / "energy.txt").is_file():
        raise RuntimeError(
            "PSolver did not produce output (its Fortran STOP may return zero):\n"
            + run.stdout
            + run.stderr
        )
    calculated = np.loadtxt(case / "potential.txt").reshape((n, n, n), order="F")
    if not np.isfinite(calculated).all():
        raise RuntimeError("PSolver produced nonfinite potential")
    mean = float(calculated.mean())
    # Periodic potentials are defined up to a constant. Compare the zero-mean gauges.
    error = calculated - mean - reference + float(reference.mean())
    actual_energy = float((case / "energy.txt").read_text())
    if not np.isfinite(actual_energy):
        raise RuntimeError("PSolver produced nonfinite energy")
    expected_energy = float(3 * np.pi**2 / 8)
    return {
        "grid": [n, n, n],
        "spacing_bohr": float(2 * np.pi / n),
        "normalization": normalization,
        "max_error": float(np.max(np.abs(error))),
        "rms_error": float(np.sqrt(np.mean(error**2))),
        "potential_mean": mean,
        "charge_integral": float(density.sum() * (2 * np.pi / n) ** 3),
        "hartree_energy": actual_energy,
        "analytical_energy": expected_energy,
        "energy_absolute_error": abs(actual_energy - expected_energy),
        "potential_sha256": sha256((case / "potential.txt").read_bytes()).hexdigest(),
        "density_sha256": sha256((case / "density.txt").read_bytes()).hexdigest(),
    }


def investigate(work: Path, *, backend: str, image: str = PINNED_IMAGE, grids=(16, 24, 32, 48)):
    runtime = compile_solver(work, backend=backend, image=image)
    results = [run_case(runtime, n) for n in grids]
    failed = run_case(runtime, 16, normalization="mathematical")
    # The work directory is operational state, not portable scientific provenance.
    provenance = {key: value for key, value in runtime.items() if key != "work"}
    return {
        "settings_version": "1.0",
        "equation": "-laplacian(V)=4*pi*rho",
        "analytical_potential": "sin(x)*sin(y)*sin(z)",
        "cell_bohr": [float(2 * np.pi)] * 3,
        "gauge": "zero mean",
        "boundary": "periodic in all three directions",
        "isf_order": 16,
        "screening": 0.0,
        "acceleration": "none",
        "mpi_ranks": 1,
        "omp_threads": 1,
        "runtime": provenance,
        "results": results,
        "rejected_normalization": failed,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--backend", choices=["docker", "native"], required=True)
    parser.add_argument("--image", default=PINNED_IMAGE)
    options = parser.parse_args()
    print(
        json.dumps(
            investigate(options.work.resolve(), backend=options.backend, image=options.image),
            indent=2,
        )
    )
