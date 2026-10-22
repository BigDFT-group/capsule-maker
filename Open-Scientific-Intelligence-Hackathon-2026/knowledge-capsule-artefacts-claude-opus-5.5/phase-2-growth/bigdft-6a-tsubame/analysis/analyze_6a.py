#!/usr/bin/env python3
"""Parse BigDFT logs of the 6a runs and compute Delta-SCF triplet energies.

Usage: analyze_6a.py RUNS_DIR [OUT_JSON]
RUNS_DIR contains one sub-directory per input name with log-<name>.yaml.
Reads logs as text (stdlib only); never executes anything from the capsule.
"""
import json
import re
import sys
from pathlib import Path

HA_EV = 27.211386245988
HA_KJ = 2625.4996394799
TARGET_EV, WINDOW_EV = 2.79, 0.15  # dec-criteria-ok

NAME = re.compile(r"6a_(?P<geo>\w+?)_(?P<state>S0|T1)_(?P<xc>pbe0?)_h(?P<h>[\d.]+)_r(?P<r>[\d-]+)$")


def grab(pattern, text, last=True, cast=str):
    found = re.findall(pattern, text, re.M)
    return cast(found[-1] if last else found[0]) if found else None


def parse(log):
    t = log.read_text(errors="replace")
    return {
        "energy_Ha": grab(r"^\s*Energy \(Hartree\)\s*:\s*(\S+)", t, cast=float),
        "mpi": grab(r"Number of MPI tasks\s*:\s*(\d+)", t, last=False, cast=int),
        "omp": grab(r"Maximal OpenMP threads per MPI task\s*:\s*(\d+)", t, last=False, cast=int),
        "electrons": grab(r"Total Number of Electrons\s*:\s*(\d+)", t, last=False, cast=int),
        "ixc": grab(r"^\s*ixc\s*:\s*(\S+)", t, last=False),
        "magnetization": grab(r"Total magnetization\s*:\s*(\S+)", t, cast=float),
        "last_gnrm": grab(r"gnrm:\s*([\d.E+-]+)", t, cast=float),
        "scf_iters": len(re.findall(r"^\s*iter:\s*\d+", t, re.M)),
        "walltime": grab(r"Walltime since initialization\s*:\s*(\S+)", t),
        "finished": "Walltime since initialization" in t,
    }


def main():
    runs = Path(sys.argv[1])
    data = {}
    for d in sorted(p for p in runs.iterdir() if p.is_dir()):
        log = d / f"log-{d.name}.yaml"
        m = NAME.match(d.name)
        if m and log.exists():
            data[d.name] = {**m.groupdict(), **parse(log)}

    pairs = {}
    for name, r in data.items():
        if r["state"] != "S0":
            continue
        t1 = data.get(name.replace("_S0_", "_T1_"))
        if not t1 or r["energy_Ha"] is None or t1["energy_Ha"] is None:
            continue
        de = t1["energy_Ha"] - r["energy_Ha"]
        key = name.replace("_S0_", "_")
        pairs[key] = {"geo": r["geo"], "xc": r["xc"], "hgrid": float(r["h"]), "rmult": r["r"],
                      "E_S0_Ha": r["energy_Ha"], "E_T1_Ha": t1["energy_Ha"],
                      "dE_Ha": de, "dE_eV": de * HA_EV, "dE_kJ_mol": de * HA_KJ,
                      "vs_target_eV": de * HA_EV - TARGET_EV}

    out = {"runs": data, "pairs": pairs, "target_eV": TARGET_EV, "window_eV": WINDOW_EV}
    print(f"{'run':38s} {'E(Ha)':>20s} {'mag':>5s} {'iters':>5s} {'gnrm':>9s} {'wall':>16s}")
    for n, r in data.items():
        print(f"{n:38s} {r['energy_Ha'] or float('nan'):20.10f} {r['magnetization'] or 0:5.2f} "
              f"{r['scf_iters']:5d} {r['last_gnrm'] or 0:9.2e} {r['walltime'] or 'UNFINISHED':>16s}")
    print(f"\n{'pair':34s} {'dE (eV)':>9s} {'kJ/mol':>8s} {'vs 2.79':>8s}")
    for k, p in sorted(pairs.items(), key=lambda kv: (kv[1]["xc"], -kv[1]["hgrid"], kv[1]["rmult"])):
        print(f"{k:34s} {p['dE_eV']:9.4f} {p['dE_kJ_mol']:8.2f} {p['vs_target_eV']:+8.3f}")
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
