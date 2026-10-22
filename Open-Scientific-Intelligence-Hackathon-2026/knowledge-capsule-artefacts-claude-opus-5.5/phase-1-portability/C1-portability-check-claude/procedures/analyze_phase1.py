"""Phase 1 analysis (stdlib): adiabatic PBE Delta-SCF triplet energy of thioxanthone from the packaged BigDFT runs.

Run from the capsule root: python procedures/analyze_phase1.py   -> prints a JSON summary
PBE: energies are the last GEOPT_SQNM line of data-*/geopt.mon; geometries come from final_*.yaml.
PBE0 (Phase 1b): single points at the PBE geometries; energy = last "Energy (Hartree)" of the log.
Thioxanthone atom order (bigdft/thioxanthone_gfn2.xyz): O0, C1 (=C9), ring A C2-C7, S8, ring B C9-C14, H15-H22.
"""
import json
import math
import re
from pathlib import Path

RUNS = Path("bigdft/runs")
HA_EV, HA_KJ = 27.211386, 2625.4996
EXP_TX_KJ, EXP_6A_KJ = 274.1, 269.0


def last_energy(name):
    mon = (RUNS / name / f"data-{name}" / "geopt.mon").read_text().splitlines()
    rows = [l.split() for l in mon if "GEOPT_SQNM" in l]
    assert any("converged" in l for l in mon), f"{name}: SQNM did not converge"
    return float(rows[-1][3]), float(rows[-1][5]), len(rows)


def sp_energy(name):
    log = (RUNS / name / f"log-{name}.yaml").read_text()
    if "_T1_" in name:
        assert "Total magnetization             :  2.000000" in log, f"{name}: not a triplet"
    return float(re.findall(r"^ Energy \(Hartree\) +: +(\S+)", log, re.M)[-1])


def conv(de):
    return dict(Ha=round(de, 8), eV=round(de * HA_EV, 4), kJ_mol=round(de * HA_KJ, 2))


def positions(name):
    text = (RUNS / name / f"final_{name}.yaml").read_text()
    return [(e, tuple(map(float, xyz.split(","))))
            for e, xyz in re.findall(r"- ([A-Z][a-z]?): \[([^\]]+)\]", text)]


def d(p, i, j):
    return math.dist(p[i][1], p[j][1])


def normal(p, a, b, c):
    u = [p[b][1][k] - p[a][1][k] for k in range(3)]
    v = [p[c][1][k] - p[a][1][k] for k in range(3)]
    n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    s = math.sqrt(sum(x * x for x in n))
    return [x / s for x in n]


def geometry(p):
    na, nb = normal(p, 2, 4, 6), normal(p, 9, 11, 13)  # outer benzo rings
    fold = math.degrees(math.acos(min(1.0, abs(sum(x * y for x, y in zip(na, nb))))))
    return dict(C9_O=round(d(p, 0, 1), 4), C_S=[round(d(p, 8, 7), 4), round(d(p, 8, 9), 4)],
                C9_Cring=[round(d(p, 1, 2), 4), round(d(p, 1, 14), 4)], ring_fold_deg=round(fold, 2))


if __name__ == "__main__":
    out = {}
    for st in ("S0", "T1"):
        name = f"tx_{st}_pbe_geopt"
        e, fmax, n = last_energy(name)
        p = positions(name)
        assert len(p) == 23 and sum(x[0] == "H" for x in p) == 8
        out[st] = dict(energy_Ha=e, fmax_Ha_per_bohr=fmax, sqnm_steps=n, geometry=geometry(p))
    de = out["T1"]["energy_Ha"] - out["S0"]["energy_Ha"]
    out["adiabatic_PBE"] = dict(conv(de), vs_thioxanthone_lit_kJ=round(de * HA_KJ - EXP_TX_KJ, 2),
                                vs_6a_exp_kJ=round(de * HA_KJ - EXP_6A_KJ, 2))
    e = {f"{st}@{g}": sp_energy(f"tx_{st}_pbe0_at_{g}pbe") for st in ("S0", "T1") for g in ("S0", "T1")}
    out["PBE0_energies_Ha"] = e
    ad = e["T1@T1"] - e["S0@S0"]
    out["PBE0"] = dict(
        adiabatic=dict(conv(ad), vs_thioxanthone_lit_kJ=round(ad * HA_KJ - EXP_TX_KJ, 2),
                       vs_thioxanthone_lit_eV=round((ad * HA_KJ - EXP_TX_KJ) / HA_KJ * HA_EV, 4),
                       vs_6a_exp_kJ=round(ad * HA_KJ - EXP_6A_KJ, 2)),
        vertical_absorption_T1_at_S0=conv(e["T1@S0"] - e["S0@S0"]),
        vertical_emission_at_T1=conv(e["T1@T1"] - e["S0@T1"]),
        relaxation_T1=conv(e["T1@S0"] - e["T1@T1"]),
        relaxation_S0=conv(e["S0@T1"] - e["S0@S0"]))
    cal = abs(ad * HA_KJ - EXP_TX_KJ) / HA_KJ * HA_EV
    out["calibration"] = dict(PBE_miss_eV=round(abs(de * HA_KJ - EXP_TX_KJ) / HA_KJ * HA_EV, 4),
                              PBE0_miss_eV=round(cal, 4), window_eV=0.2, PBE0_passes=cal <= 0.2)
    print(json.dumps(out, indent=1))
