"""Collect the NLCC thioxanthone energies and compare with capsule C1 (Krack PBE pseudopotentials).

    python -I nlcc_tx/analyze_nlcc.py C1 nlcc_tx      # writes nlcc_tx/nlcc_summary.json
Stdlib only. Final energy = last 'Energy (Hartree)' in each log; convergence = last gnrm < gnrm_cv.
"""
import json
import re
import sys
from pathlib import Path

C1, W = Path(sys.argv[1]), Path(sys.argv[2])
HA_EV, HA_KJ = 27.211386245988, 2625.4996394799
LIT_TX_KJ, EXP_6A_KJ, WINDOW_EV = 274.1, 269.0, 0.2


def read(log):
    t = log.read_text()
    found = re.findall(r"Energy \(Hartree\)\s*:\s*(\S+)", t)
    if not found:  # still running
        return None
    e = float(found[-1].replace("D", "E"))
    gnrm = [float(g) for g in re.findall(r"gnrm:\s*(\S+?),", t)]
    mag = re.findall(r"Total magnetization\s*:\s*(\S+)", t)
    itermax = int(re.search(r"itermax\s*:\s*(\d+)", t).group(1))
    # gnrm is printed with 3 digits, so trust BigDFT's own stop (#FINAL) below itermax rather than the rounded value
    final = re.findall(r"iter:\s*(\d+),.*gnrm:.*#FINAL", t)
    converged = bool(final) and int(final[-1]) < itermax and gnrm[-1] <= 1e-5
    return dict(energy_Ha=e, last_gnrm=gnrm[-1] if gnrm else None, converged=converged,
                scf_iterations=len(gnrm), magnetization=float(mag[-1]) if mag else None)


def gap(e_hi, e_lo):
    d = e_hi - e_lo
    return dict(Ha=round(d, 8), eV=round(d * HA_EV, 4), kJ_mol=round(d * HA_KJ, 2))


runs = {p.name: read(p / f"log-{p.name}.yaml") for p in sorted((W / "runs").iterdir())
        if p.is_dir() and (p / f"log-{p.name}.yaml").exists()}
runs = {k: v for k, v in runs.items() if v}
c1 = json.loads((C1 / "bigdft" / "runs" / "phase1_summary.json").read_text())
out = {"runs": runs}
ctl = {"S0": runs.get("tx_S0_pbe_krack_at_S0pbe"), "T1": runs.get("tx_T1_pbe_krack_at_T1pbe")}
out["control_vs_C1_Ha"] = {s: (r["energy_Ha"] - c1[s]["energy_Ha"]) if r else None for s, r in ctl.items()}

for xc in ("pbe", "pbe0"):
    E = {k: runs.get(f"tx_{k[:2]}_{xc}_nlcc_at_{k[3:]}pbe", {}).get("energy_Ha") for k in
         ("S0@S0", "S0@T1", "T1@S0", "T1@T1")}
    res = {"energies_Ha": E}
    if E["S0@S0"] is not None and E["T1@T1"] is not None:
        ad = gap(E["T1@T1"], E["S0@S0"])
        ref = c1["adiabatic_PBE"] if xc == "pbe" else c1["PBE0"]["adiabatic"]
        res["adiabatic"] = dict(ad, vs_thioxanthone_lit_kJ=round(ad["kJ_mol"] - LIT_TX_KJ, 2),
                                vs_thioxanthone_lit_eV=round(ad["eV"] - LIT_TX_KJ / HA_KJ * HA_EV, 4),
                                vs_6a_exp_kJ=round(ad["kJ_mol"] - EXP_6A_KJ, 2),
                                nlcc_minus_krack_kJ=round(ad["kJ_mol"] - ref["kJ_mol"], 2),
                                nlcc_minus_krack_eV=round(ad["eV"] - ref["eV"], 4),
                                passes_calibration=abs(ad["eV"] - LIT_TX_KJ / HA_KJ * HA_EV) <= WINDOW_EV)
    if E["T1@S0"] is not None and E["S0@S0"] is not None:
        res["vertical_absorption_T1_at_S0"] = gap(E["T1@S0"], E["S0@S0"])
    if E["T1@T1"] is not None and E["S0@T1"] is not None:
        res["vertical_emission_at_T1"] = gap(E["T1@T1"], E["S0@T1"])
    if E["T1@S0"] is not None and E["T1@T1"] is not None:
        res["relaxation_T1"] = gap(E["T1@S0"], E["T1@T1"])
    if E["S0@T1"] is not None and E["S0@S0"] is not None:
        res["relaxation_S0"] = gap(E["S0@T1"], E["S0@S0"])
    out[xc.upper() + "_NLCC"] = res

(W / "nlcc_summary.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
