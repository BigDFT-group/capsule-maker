#!/usr/bin/env python3
"""Condense the Phase 2 BigDFT logs into compact, checksummed evidence (stdlib only).

Usage: collect_evidence.py RESULTS_DIR OUT_DIR
  RESULTS_DIR  local copy of the TSUBAME results (stage sub-directories 00_... 07_, dryruns/)
  OUT_DIR      writes energies.json, dryruns.json and geometries/*.xyz

Every run entry records the SHA-256 of its full log, so the condensed numbers can be
checked against the external log archive. Nothing from the logs is executed.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

GEOMETRIES = {  # output name -> final geometry file (relative to RESULTS_DIR)
    "6a_cgS0_pbe.xyz": "05_geopt_constrained/6a_S0_pbe_cgeopt/final_6a_S0_pbe_cgeopt.yaml",
    "6a_cgT1_pbe.xyz": "05_geopt_constrained/6a_T1_pbe_cgeopt/final_6a_T1_pbe_cgeopt.yaml",
    "6a_freeS0_pbe.xyz": "04_geopt_free/6a_S0_pbe_geopt/final_6a_S0_pbe_geopt.yaml",
}


def grab_all(pattern, text):
    return re.findall(pattern, text, re.M)


def parse_log(path):
    t = path.read_text(errors="replace")
    energies = [float(x) for x in grab_all(r"^\s*Energy \(Hartree\)\s*:\s*(\S+)", t)]
    gnrm = grab_all(r"^\s*iter:\s*\d+,.*?gnrm:\s*([\d.E+-]+)", t)
    fmax = grab_all(r"FORCES norm\(Ha/Bohr\): \{ maxval:\s*([\d.E+-]+),.*?fluct:\s*([\d.E+-]+)", t)
    first = lambda p, cast=str: (lambda v: cast(v[0]) if v else None)(grab_all(p, t))
    entry = {
        "log_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "log_bytes": path.stat().st_size,
        "finished": "Walltime since initialization" in t,
        "ixc": first(r"^\s*ixc\s*:\s*(\S+)"),
        "mpi_tasks": first(r"Number of MPI tasks\s*:\s*(\d+)", int),
        "omp_threads": first(r"Maximal OpenMP threads per MPI task\s*:\s*(\d+)", int),
        "electrons": first(r"Total Number of Electrons\s*:\s*(\d+)", int),
        "energy_Ha": energies[-1] if energies else None,
        "energy_evaluations": len(energies),
        "scf_iterations_total": len(grab_all(r"^\s*iter:\s*\d+", t)),
        "last_gnrm": float(gnrm[-1]) if gnrm else None,
        "magnetization": (lambda v: float(v[-1]) if v else None)(grab_all(r"Total magnetization\s*:\s*(\S+)", t)),
        "walltime": (lambda v: v[-1] if v else None)(grab_all(r"Walltime since initialization\s*:\s*(\S+)", t)),
    }
    if fmax:
        entry["final_fmax_Ha_bohr"] = float(fmax[-1][0])
        entry["final_force_fluct_Ha_bohr"] = float(fmax[-1][1])
        entry["sqnm_converged"] = "SQNM converged" in t
    return entry


def xyz_from_final(path):
    """BigDFT final_*.yaml (units angstroem) -> plain 4-column XYZ text."""
    atoms = re.findall(r"^ - ([A-Z][a-z]?): \[([^\]]+)\]", path.read_text(), re.M)
    lines = [str(len(atoms)), f"from {path.name}, Angstrom"]
    lines += [f"{el} " + " ".join(c.strip() for c in xyz.split(",")) for el, xyz in atoms]
    return "\n".join(lines) + "\n"


def main():
    res, out = Path(sys.argv[1]), Path(sys.argv[2])
    runs = {}
    for stage in sorted(p for p in res.iterdir() if p.is_dir() and re.match(r"\d\d_", p.name)):
        for run in sorted(p for p in stage.iterdir() if p.is_dir()):
            log = run / f"log-{run.name}.yaml"
            if log.exists():
                runs[f"{stage.name}/{run.name}"] = parse_log(log)
    (out / "energies.json").write_text(json.dumps(runs, indent=1) + "\n")

    dry = {}
    for stage in sorted((res / "dryruns").iterdir()):
        for mem in sorted(stage.glob("mem-*.txt")):
            t = mem.read_text(errors="replace")
            peak = re.findall(r"Estimated Memory Peak \(MB\)\s*:\s*(\d+)", t)
            dry[f"{stage.name}/{mem.stem[4:]}"] = {
                "estimated_peak_MB_per_process_16proc": int(peak[0]) if peak else None,
                "electrons": (lambda v: int(v[0]) if v else None)(re.findall(r"Total Number of Electrons\s*:\s*(\d+)", t)),
                "bigdft_error_block": bool(re.search(r"BigDFT_.*ERROR|Error code|Additional Info", t)),
            }
    (out / "dryruns.json").write_text(json.dumps(dry, indent=1) + "\n")

    (out.parent / "geometries").mkdir(exist_ok=True)
    for name, rel in GEOMETRIES.items():
        (out.parent / "geometries" / name).write_text(xyz_from_final(res / rel))
    print(f"{len(runs)} runs, {len(dry)} dry runs, {len(GEOMETRIES)} geometries")


if __name__ == "__main__":
    main()
