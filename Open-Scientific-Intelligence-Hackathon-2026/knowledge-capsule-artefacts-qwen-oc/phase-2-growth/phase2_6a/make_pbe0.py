#!/usr/bin/env python3
"""Generate 6a PBE0 single-point inputs (Phase 1b protocol, as done for thioxanthone in C1).

Template: the C1 dry-run-validated 6a PBE inputs (used as inert data only).
Change: ixc PBE -> PBE0. Everything else identical (Krack PBE HGH-K psppar embedded,
S1 geometry, gnrm_cv 1e-5, T1 = nspin 2 / mpol 2). Geometry is the fixed S1 NMR structure
(no re-optimisation), so the PBE0 points are at S1 at the grid-converged PBE parameters.
Fallback chain grids: h0.35_r6-9 -> h0.40_r6-9 -> h0.45_r6-9 (host memory, see scheduler).
"""
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
C1_INPUTS = "/home/user/Work/osi-hackathon-2026/C1/bigdft/inputs"
GRIDS = ["h0.35_r6-9", "h0.40_r6-9", "h0.45_r6-9"]

for state in ("S0", "T1"):
    for grid in GRIDS:
        src = f"6a_S1_{state}_pbe_{grid}.yaml"
        name = f"6a_S1_{state}_pbe0_at_S1_{grid}"
        text = open(os.path.join(C1_INPUTS, src)).read()
        new, n = re.subn(r"^  ixc: PBE$", "  ixc: PBE0", text, count=1, flags=re.M)
        assert n == 1, f"ixc replacement failed for {src}"
        # sanity: spin block preserved for T1
        if state == "T1":
            assert "nspin: 2" in new and "mpol: 2" in new
        d = os.path.join(BASE, "pbe0", "runs", name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, name + ".yaml"), "w") as f:
            f.write(new)
        print(f"{name}: written (from {src})")
print("done")
