"""Generate the BigDFT input files (self-contained YAML: dft/geopt + embedded posinp + psppar) for the E_T study.

Needs PyBigDFT (tested with 1.9.6) and PyYAML. Run from the capsule root:
    python procedures/make_inputs.py            # writes bigdft/inputs/<name>.yaml and bigdft/inputs/index.json
Phase 1: thioxanthone S0 and T1 geometry optimisations (PBE).
Phase 2: 6a S1 S0/T1 single points over an hgrid x rmult grid (PBE), for convergence of E(T1) - E(S0).
Phase 1b: thioxanthone PBE0 single points at the converged PBE S0 and T1 geometries (bigdft/runs/*/final_*.yaml):
adiabatic (S0@S0, T1@T1) and vertical (T1@S0 absorption, S0@T1 emission).
"""
import json
from pathlib import Path

import yaml
from BigDFT.Inputfiles import Inputfile

BD = Path("bigdft")
OUT = BD / "inputs"
ELEMENTS = "CHNOS"


def positions(xyz):
    if xyz.endswith(".yaml"):  # BigDFT final geometry (Angstrom)
        pos = yaml.safe_load((BD / xyz).read_text())["positions"]
        return [{e: [float(c) for c in v]} for p in pos for e, v in p.items() if e != "force"]
    lines = (BD / xyz).read_text().splitlines()
    n = int(lines[0])
    return [{e: [float(x), float(y), float(z)]} for e, x, y, z in (l.split() for l in lines[2:2 + n])]


def make(xyz, state, hgrid, rmult, geopt=False, xc="PBE"):
    inp = Inputfile()
    inp.set_xc(xc)
    inp.set_hgrid(hgrid)
    inp.set_rmult(coarse=rmult[0], fine=rmult[1])
    inp.set_scf_convergence(gnrm=1.0e-5)
    if state == "T1":
        inp.spin_polarize(mpol=2)  # lowest triplet as a Delta-SCF ground state
    if geopt:
        inp.optimize_geometry(method="SQNM", nsteps=300, betax=1.0, forcemax=2.0e-4)
    pos = positions(xyz)
    present = {next(iter(p)) for p in pos}
    # set_psp_krack(elements=...) is a silent no-op in PyBigDFT 1.9.6; load each file explicitly
    for e in ELEMENTS:
        if e in present:
            inp.set_psp_file(filename=str(BD / "psppar" / f"psppar.{e}.yaml"), element=e)
    assert {k[len("psppar."):] for k in inp if k.startswith("psppar.")} == present, "missing pseudopotential"
    inp.set_atomic_positions({"units": "angstroem", "positions": pos})
    return inp


RUNS = {}
for st in ("S0", "T1"):
    RUNS[f"tx_{st}_pbe_geopt"] = ("thioxanthone_gfn2.xyz", st, 0.35, (6.0, 9.0), True)
for h in (0.45, 0.40, 0.35, 0.30):
    for rm in ((5.0, 8.0), (6.0, 9.0), (7.0, 10.0)):
        for st in ("S0", "T1"):
            RUNS[f"6a_S1_{st}_pbe_h{h:.2f}_r{rm[0]:.0f}-{rm[1]:.0f}"] = ("6a_S1.xyz", st, h, rm, False)
for st in ("S0", "T1"):
    for geo in ("S0", "T1"):
        RUNS[f"tx_{st}_pbe0_at_{geo}pbe"] = (f"runs/tx_{geo}_pbe_geopt/final_tx_{geo}_pbe_geopt.yaml", st, 0.35,
                                             (6.0, 9.0), False, "PBE0")

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    index = {}
    for name, (xyz, st, h, rm, geo, *xc) in RUNS.items():
        inp = make(xyz, st, h, rm, geo, *xc)
        (OUT / f"{name}.yaml").write_text(yaml.safe_dump(dict(inp), sort_keys=False, default_flow_style=None))
        index[name] = dict(structure=f"bigdft/{xyz}", state=st, hgrid=h, rmult=list(rm), geopt=geo, xc=(xc or ["PBE"])[0])
    (OUT / "index.json").write_text(json.dumps(index, indent=1) + "\n")
    print(f"wrote {len(index)} inputs to {OUT}")
