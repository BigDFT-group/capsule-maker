#!/usr/bin/env python3
"""Parse phase2_6a run logs; build PBE grid-convergence table + PBE0 E_T; compare to target 2.79 +/- 0.15 eV.

E_T = E(T1) - E(S0), adiabatic Delta-SCF (single points at the fixed S1 geometry per grid point).
Constants: 1 Ha = 27.211386248 eV = 2625.497 kJ/mol (same as the tx_nlcc/analyze.py convention).
Writes results.json next to this file; prints it.
"""
import glob
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
HA_EV = 27.211386248
HA_KJ = 2625.497
TARGET_EV, WINDOW_EV = 2.79, 0.15
TARGET_KJ = 269.0

def parse_log(path):
    final, last = None, None
    with open(path) as f:
        for line in f:
            m = re.search(r"EKS:\s*(-?\d+\.?\d*(?:[eE][+-]?\d+)?)", line)
            if m:
                last = float(m.group(1))
                if "#FINAL" in line:
                    final = float(m.group(1))
    return final if final is not None else last

def collect(pattern_dir, name_re, keyfn):
    out = {}
    for d in sorted(glob.glob(os.path.join(BASE, pattern_dir, "*"))):
        name = os.path.basename(d)
        m = re.match(name_re, name)
        if not m:
            continue
        logp = os.path.join(d, f"log-{name}.yaml")
        if not os.path.exists(logp):
            continue
        try:
            v = parse_log(logp)
        except OSError:
            continue
        if v is None:
            continue
        out.setdefault(keyfn(*m.groups()), {})[m.group(1)] = v
    return out

def et_block(d):
    e = {"E_S0_Ha": d.get("S0"), "E_T1_Ha": d.get("T1")}
    if d.get("S0") is not None and d.get("T1") is not None:
        et = d["T1"] - d["S0"]
        e["E_T_Ha"] = round(et, 9)
        e["E_T_eV"] = round(et * HA_EV, 6)
        e["E_T_kJ_mol"] = round(et * HA_KJ, 2)
    return e

def main():
    pbe = collect("runs", r"6a_S1_(S0|T1)_pbe_(h0\.\d+)_r(\d-\d)$",
                  lambda st, hg, rm: f"PBE_{hg}_r{rm}")
    pbe0 = collect("pbe0/runs", r"6a_S1_(S0|T1)_pbe0_at_S1_(h0\.\d+_r\d-\d)$",
                   lambda st, hg: f"PBE0_{hg}")
    out = {
        "target": {"E_T_eV": TARGET_EV, "window_eV": WINDOW_EV, "E_T_kJ_mol": TARGET_KJ},
        "pbe_grid": {k: et_block(v) for k, v in sorted(pbe.items())},
        "pbe0": {k: et_block(v) for k, v in sorted(pbe0.items())},
    }
    for k, v in out["pbe0"].items():
        if "E_T_eV" in v:
            v["vs_target"] = {
                "diff_eV": round(v["E_T_eV"] - TARGET_EV, 6),
                "diff_kJ_mol": round(v["E_T_kJ_mol"] - TARGET_KJ, 2),
                "within_window": abs(v["E_T_eV"] - TARGET_EV) <= WINDOW_EV,
            }
    with open(os.path.join(BASE, "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
