#!/usr/bin/env python3
"""Collect the key 6a energies from results/ and compute vertical and adiabatic E_T.

Usage: python3 analysis/summarize.py   (from bigdft-6a-tsubame/; writes analysis/summary.json)
Only finished runs (log contains 'Walltime since initialization') are used; others are listed as pending.
"""
import json
import re
from pathlib import Path

HA_EV = 27.211386245988
HA_KJ = 2625.4996394799
TARGET_EV, WINDOW_EV = 2.79, 0.15  # capsule dec-criteria-ok

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"

# label -> run directory (relative to results/)
RUNS = {
    "PBE S0@S1": "02_pbe_s1_wavefunctions/6a_S1_S0_pbe_h0.35_r6-9",
    "PBE T1@S1": "02_pbe_s1_wavefunctions/6a_S1_T1_pbe_h0.35_r6-9",
    "PBE S0@cgS0": "05_geopt_constrained/6a_S0_pbe_cgeopt",
    "PBE T1@cgT1": "05_geopt_constrained/6a_T1_pbe_cgeopt",
    "PBE T1@cgS0": "06_pbe_cg_wavefunctions/6a_cgS0_T1_pbe_h0.35_r6-9",
    "PBE S0@cgT1": "06_pbe_cg_wavefunctions/6a_cgT1_S0_pbe_h0.35_r6-9",
    "PBE S0@freeS0": "04_geopt_free/6a_S0_pbe_geopt",
    "PBE0 S0@S1": "03_pbe0_s1_vertical/6a_S1_S0_pbe0_h0.35_r6-9",
    "PBE0 T1@S1": "03_pbe0_s1_vertical/6a_S1_T1_pbe0_h0.35_r6-9",
    "PBE0 S0@cgS0": "07_pbe0_cg/6a_cgS0_S0_pbe0_h0.35_r6-9",
    "PBE0 T1@cgT1": "07_pbe0_cg/6a_cgT1_T1_pbe0_h0.35_r6-9",
    "PBE0 T1@cgS0": "07_pbe0_cg/6a_cgS0_T1_pbe0_h0.35_r6-9",
    "PBE0 S0@cgT1": "07_pbe0_cg/6a_cgT1_S0_pbe0_h0.35_r6-9",
}

# label -> (upper state run, lower state run)
GAPS = {
    "PBE vertical at S1": ("PBE T1@S1", "PBE S0@S1"),
    "PBE adiabatic (constrained)": ("PBE T1@cgT1", "PBE S0@cgS0"),
    "PBE vertical absorption at cgS0": ("PBE T1@cgS0", "PBE S0@cgS0"),
    "PBE vertical emission at cgT1": ("PBE T1@cgT1", "PBE S0@cgT1"),
    "PBE0 vertical at S1": ("PBE0 T1@S1", "PBE0 S0@S1"),
    "PBE0 adiabatic (constrained) [criterion]": ("PBE0 T1@cgT1", "PBE0 S0@cgS0"),
    "PBE0 vertical absorption at cgS0": ("PBE0 T1@cgS0", "PBE0 S0@cgS0"),
    "PBE0 vertical emission at cgT1": ("PBE0 T1@cgT1", "PBE0 S0@cgT1"),
}


def final_energy(run_dir):
    logs = list((RES / run_dir).glob("log-*.yaml"))
    if not logs:
        return None
    text = logs[0].read_text(errors="replace")
    if "Walltime since initialization" not in text:
        return None
    found = re.findall(r"^\s*Energy \(Hartree\)\s*:\s*(\S+)", text, re.M)
    return float(found[-1]) if found else None


def main():
    energies = {k: final_energy(v) for k, v in RUNS.items()}
    gaps = {}
    for label, (hi, lo) in GAPS.items():
        if energies[hi] is None or energies[lo] is None:
            gaps[label] = None
            continue
        d = energies[hi] - energies[lo]
        gaps[label] = {"Ha": d, "eV": d * HA_EV, "kJ_mol": d * HA_KJ,
                       "vs_target_eV": d * HA_EV - TARGET_EV,
                       "within_window": abs(d * HA_EV - TARGET_EV) <= WINDOW_EV}

    print(f"{'run':16s} {'E (Ha)':>20s}")
    for k, e in energies.items():
        print(f"{k:16s} {e:20.10f}" if e is not None else f"{k:16s} {'pending':>20s}")
    print(f"\n{'E_T':42s} {'eV':>7s} {'kJ/mol':>8s} {'vs 2.79':>8s}")
    for k, g in gaps.items():
        if g is None:
            print(f"{k:42s} {'pending':>7s}")
        else:
            print(f"{k:42s} {g['eV']:7.4f} {g['kJ_mol']:8.2f} {g['vs_target_eV']:+8.3f}")
    out = {"energies_Ha": energies, "E_T": gaps, "target_eV": TARGET_EV, "window_eV": WINDOW_EV}
    (ROOT / "analysis" / "summary.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
