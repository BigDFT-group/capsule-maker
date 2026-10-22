import sys
"""GFN2-xTB / ALPB(CH2Cl2) local relaxation of the NMR-restrained 6a structure, then re-check Table S1 restraints."""
from ase.io import read, write
from ase.constraints import FixConstraint
import numpy as np
from ase.optimize import BFGS
from tblite.ase import TBLite
from rdkit import Chem
from rdkit.Geometry import Point3D
import build_6a as b


class FlatBottom(FixConstraint):
    """Harmonic penalty k*(d-lo)^2 below lo and k*(d-hi)^2 above hi on atom pair (i, j); zero in between."""
    def __init__(self, i, j, lo, hi, k):
        self.i, self.j, self.lo, self.hi, self.k = i, j, lo, hi, k

    def _x(self, atoms):
        v = atoms.positions[self.j] - atoms.positions[self.i]
        d = np.linalg.norm(v)
        return v / d, min(d - self.lo, 0) + max(d - self.hi, 0)

    def adjust_positions(self, atoms, new):
        pass

    def adjust_forces(self, atoms, forces):
        u, x = self._x(atoms)
        forces[self.i] += 2 * self.k * x * u
        forces[self.j] -= 2 * self.k * x * u

    def adjust_potential_energy(self, atoms):
        return self.k * self._x(atoms)[1] ** 2

    def get_removed_dof(self, atoms):
        return 0

    def todict(self):
        return {"name": "FlatBottom", "kwargs": vars(self)}

restrained = "--free" not in sys.argv
tag = "6a_nmr_gfn2_ch2cl2" + ("_restrained" if restrained else "")
atoms = read("6a_nmr_restrained_mmff.xyz")
if restrained:  # Table S1 bounds: upper on the closest pair (group = min distance), lower on every pair
    m0 = Chem.MolFromMolFile("6a_nmr_restrained_mmff.mol", removeHs=False); b.mol = m0; c0 = m0.GetConformer()
    cons = []
    for a, bb, lo, hi in b.SETS[b.score(c0)[3]]:
        i, j = min(((i, j) for i in a for j in bb), key=lambda ij: atoms.get_distance(*ij))
        cons.append(FlatBottom(i, j, 0.0, hi, 2.5))
        cons += [FlatBottom(i, j, lo, 99.0, 2.5) for i in a for j in bb]
    atoms.set_constraint(cons)
atoms.calc = TBLite(method="GFN2-xTB", solvation=("alpb", "dichloromethane"), verbosity=0)
BFGS(atoms, logfile=tag + ".log").run(fmax=0.02, steps=2000)
print(f"E(GFN2/ALPB CH2Cl2) = {atoms.get_potential_energy():.4f} eV")
atoms.set_constraint()
write(tag + ".xyz", atoms, comment="6a (R,R,S)-Pga-Pro-Aib-pTxa-OMe, NMR-restrained start, GFN2-xTB/ALPB(CH2Cl2) relaxed" + (" with Table S1 flat-bottom restraints (k=2.5 eV/A^2)" if restrained else "") + ", charge 0, singlet")

m = Chem.MolFromMolFile("6a_nmr_restrained_mmff.mol", removeHs=False)  # same atom order as the xyz
conf = m.GetConformer()
for i, p in enumerate(atoms.positions):
    conf.SetAtomPosition(i, Point3D(*p))
b.mol = m
s = b.score(conf)
print(f"restraints: sumsq {s[0]:.3f} A^2, max viol {s[1]:.2f} A, >0.3 A: {s[2]}; H...O {b.hbond(conf):.2f} A")
Chem.MolToMolFile(m, tag + ".mol")
