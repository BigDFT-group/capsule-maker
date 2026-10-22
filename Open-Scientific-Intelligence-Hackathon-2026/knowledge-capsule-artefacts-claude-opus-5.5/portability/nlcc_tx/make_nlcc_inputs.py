"""Thioxanthone Delta-SCF triplet energy with NLCC pseudopotentials at the C1 PBE geometries (no re-optimisation).

Same settings as capsule C1 Phase 1/1b (hgrid 0.35, rmult (6, 9), gnrm_cv 1e-5, free BC, T1 = nspin 2 / mpol 2).
Pseudopotentials: first the C1 Krack PBE psppar for every element present, then the PyBigDFT NLCC set
(Database/psppar/SS, Saha 2015) overwrites every element for which it exists. For thioxanthone that is C, H, O;
S has no NLCC file and keeps the C1 Krack file.

    python -I nlcc_tx/make_nlcc_inputs.py C1 nlcc_tx/inputs
"""
import json
import sys
from pathlib import Path

import yaml
from BigDFT.Inputfiles import Inputfile
from BigDFT import InputActions

C1, OUT = Path(sys.argv[1]), Path(sys.argv[2])
NLCC_DIR = Path(InputActions.__file__).parent / "Database" / "psppar" / "SS"
GEOM = {g: C1 / "bigdft" / "runs" / f"tx_{g}_pbe_geopt" / f"final_tx_{g}_pbe_geopt.yaml" for g in ("S0", "T1")}


def positions(path):
    pos = yaml.safe_load(path.read_text())["positions"]
    return [{e: [float(c) for c in v]} for p in pos for e, v in p.items() if e != "force"]


def make(geo, state, xc, nlcc):
    inp = Inputfile()
    inp.set_xc(xc)
    inp.set_hgrid(0.35)
    inp.set_rmult(coarse=6.0, fine=9.0)
    inp.set_scf_convergence(gnrm=1.0e-5)
    if state == "T1":
        inp.spin_polarize(mpol=2)
    pos = positions(GEOM[geo])
    present = sorted({next(iter(p)) for p in pos})
    # 1) C1 psppar for all elements (set_psp_file: set_psp_krack/nlcc(elements=[...]) are no-ops in PyBigDFT 1.9.6)
    for e in present:
        inp.set_psp_file(filename=str(C1 / "bigdft" / "psppar" / f"psppar.{e}.yaml"), element=e)
    # 2) NLCC overwrites every element it provides
    if nlcc:
        for e in present:
            f = NLCC_DIR / f"psppar.{e}.yaml"
            if f.exists():
                inp.set_psp_file(filename=str(f), element=e)
    assert {k[len("psppar."):] for k in inp if k.startswith("psppar.")} == set(present), "missing pseudopotential"
    inp.set_atomic_positions({"units": "angstroem", "positions": pos})
    return inp


RUNS = {}
# control: reproduce the C1 PBE/Krack energies at the converged geometries with this BigDFT build
for st in ("S0", "T1"):
    RUNS[f"tx_{st}_pbe_krack_at_{st}pbe"] = (st, st, "PBE", False)
# NLCC: full S0/T1 x geometry matrix (adiabatic + vertical) for PBE and PBE0
for xc in ("PBE", "PBE0"):
    for st in ("S0", "T1"):
        for geo in ("S0", "T1"):
            RUNS[f"tx_{st}_{xc.lower()}_nlcc_at_{geo}pbe"] = (geo, st, xc, True)

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    index = {}
    for name, (geo, st, xc, nlcc) in RUNS.items():
        inp = make(geo, st, xc, nlcc)
        (OUT / f"{name}.yaml").write_text(yaml.safe_dump(dict(inp), sort_keys=False, default_flow_style=None))
        psp = {k[len("psppar."):]: f"{v['Pseudopotential type']} ({v['Source']}), {v['No. of Electrons']} e"
               for k, v in inp.items() if k.startswith("psppar.")}
        index[name] = dict(geometry=str(GEOM[geo]), state=st, xc=xc, nlcc=nlcc, psp=psp)
    (OUT / "index.json").write_text(json.dumps(index, indent=1) + "\n")
    print(f"wrote {len(index)} inputs to {OUT}")
