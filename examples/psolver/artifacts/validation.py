"""Scientific acceptance criteria; no PSolver execution or invented measurements."""

import math


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_results(results, settings):
    _require(
        results["settings_version"] == settings["settings_version"] == "1.0",
        "Scientific validation failed: settings version",
    )
    _require(
        results["equation"] == "-laplacian(V)=4*pi*rho",
        "Scientific validation failed: Poisson equation",
    )
    _require(
        results["isf_order"] == settings["isf_order"] == 16,
        "Scientific validation failed: ISF order",
    )
    _require(results["gauge"] == "zero mean", "Scientific validation failed: zero-mean gauge")
    _require(
        results["screening"] == 0.0 and results["acceleration"] == "none",
        "Scientific validation failed: unscreened CPU settings",
    )
    _require(
        results["mpi_ranks"] == results["omp_threads"] == 1,
        "Scientific validation failed: parallel settings",
    )
    _require(
        results["cell_bohr"] == [2 * math.pi] * 3, "Scientific validation failed: periodic cell"
    )
    _require(
        results["boundary"] == "periodic in all three directions",
        "Scientific validation failed: periodic boundaries",
    )
    _require(
        results["analytical_potential"] == "sin(x)*sin(y)*sin(z)",
        "Scientific validation failed: analytical potential",
    )
    _require(
        [r["grid"][0] for r in results["results"]] == settings["grids"],
        "Scientific validation failed: grid sequence",
    )
    for row in results["results"]:
        n = row["grid"][0]
        _require(
            row["grid"] == [n] * 3 and row["normalization"] == "coulomb",
            "Scientific validation failed: grid and charge convention",
        )
        _require(
            math.isclose(row["spacing_bohr"], 2 * math.pi / n, rel_tol=1e-14),
            "Scientific validation failed: grid spacing",
        )
        _require(
            0 <= row["rms_error"] <= row["max_error"] <= settings["potential_max_error_tolerance"],
            "Scientific validation failed: potential accuracy",
        )
        _require(
            abs(row["potential_mean"]) <= settings["gauge_mean_tolerance"],
            "Scientific validation failed: potential mean",
        )
        _require(
            abs(row["charge_integral"]) <= settings["charge_integral_tolerance"],
            "Scientific validation failed: charge neutrality",
        )
        _require(
            row["analytical_energy"] == 3 * math.pi**2 / 8,
            "Scientific validation failed: analytical Hartree energy",
        )
        _require(
            math.isclose(
                row["energy_absolute_error"],
                abs(row["hartree_energy"] - row["analytical_energy"]),
                abs_tol=1e-15,
            ),
            "Scientific validation failed: energy-error consistency",
        )
        _require(
            row["energy_absolute_error"] <= settings["energy_absolute_error_tolerance"],
            "Scientific validation failed: energy accuracy",
        )
    coarse, fine = results["results"][:2]
    _require(
        fine["max_error"] < coarse["max_error"] * settings["refinement_error_ratio_limit"],
        "Scientific validation failed: coarse-to-fine error reduction",
    )
    failed = results["rejected_normalization"]
    _require(
        failed["normalization"] == "mathematical" and failed["grid"] == [16] * 3,
        "Scientific validation failed: negative-control configuration",
    )
    _require(
        math.isclose(failed["max_error"], 4 * math.pi - 1, abs_tol=1e-09),
        "Scientific validation failed: negative-control potential",
    )
    _require(
        math.isclose(
            failed["hartree_energy"], (4 * math.pi) ** 2 * 3 * math.pi**2 / 8, abs_tol=1e-08
        ),
        "Scientific validation failed: negative-control energy",
    )
    return {"accepted": True, "grids": settings["grids"], "runtime": results["runtime"]}
