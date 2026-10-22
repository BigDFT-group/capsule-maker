"""Parent 9H-thioxanthen-9-one (C13H8OS) calibration geometry: RDKit ETKDG -> MMFF94 -> gas-phase GFN2-xTB.

Pre-optimisation only; the BigDFT runs re-optimise S0 and T1 at their own level.
Run from the capsule root: uv run --with rdkit --with tblite --with ase python procedures/build_thioxanthone.py
"""
import numpy as np
from ase import Atoms
from ase.optimize import BFGS
from rdkit import Chem
from rdkit.Chem import AllChem
from tblite.ase import TBLite

SMI = "O=C1c2ccccc2Sc2ccccc21"
OUT = "bigdft/thioxanthone_gfn2.xyz"

mol = Chem.AddHs(Chem.MolFromSmiles(SMI))
p = AllChem.ETKDGv3(); p.randomSeed = 20261020
assert AllChem.EmbedMolecule(mol, p) == 0
AllChem.MMFFOptimizeMolecule(mol, maxIters=5000)
atoms = Atoms([a.GetSymbol() for a in mol.GetAtoms()], positions=mol.GetConformer().GetPositions())
atoms.calc = TBLite(method="GFN2-xTB", verbosity=0)
BFGS(atoms, logfile="bigdft/thioxanthone_gfn2.log").run(fmax=0.01, steps=1000)
e = atoms.get_potential_energy()

heavy = [i for i, s in enumerate(atoms.get_chemical_symbols()) if s != "H"]
P = atoms.positions - atoms.positions.mean(0)
plane_rms = np.linalg.svd(P[heavy])[1][-1] / np.sqrt(len(heavy))
o = atoms.get_chemical_symbols().index("O")
c9 = [n.GetIdx() for n in mol.GetAtomWithIdx(o).GetNeighbors()][0]
print(f"E(GFN2, gas) = {e:.4f} eV; heavy-atom plane rms {plane_rms:.4f} A; C9=O {atoms.get_distance(o, c9):.3f} A")

with open(OUT, "w") as f:
    f.write(f"{len(atoms)}\nthioxanthone C13H8OS, GFN2-xTB gas-phase pre-optimised (fmax 0.01 eV/A), Angstrom, charge 0\n")
    for s, (x, y, z) in zip(atoms.get_chemical_symbols(), atoms.positions):
        f.write(f"{s:<2s} {x:16.8f} {y:16.8f} {z:16.8f}\n")
print("wrote", OUT)
