"""Build an NMR-consistent 3D structure of tetrapeptide 6a, (R,R,S)-Pga-Pro-Aib-pTxa-OMe.

SMILES: Chemotion 10.14272/WQGGCBKETYIIRM-BHIFYINESA-N.2. Restraints: Table S1 (ROESY, 233 K, CD2Cl2), ids 1-33.
ETKDG conformers -> MMFF94 -> score vs restraints + type II' beta-turn H-bond (pTxa NH...O=C Pga)
-> best conformer refined with flat-bottom MMFF distance restraints.
"""
import itertools, sys
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import rdForceFieldHelpers as FF

SMI = "COC(=O)[C@@H](NC(=O)C(NC(=O)[C@H]1CCCN1C(=O)[C@H]1CCC(=O)N1)(C)C)Cc1ccc2c(c1)c(=O)c1c(s2)cccc1"
mol = Chem.AddHs(Chem.MolFromSmiles(SMI))

# heavy-atom indices in SMI (checked by the asserts below)
OME, CA_T, N_T, N_A, CA_A, CA_P, CB_P, CD_P, O_PGA, CA_G, N_G, ME1, ME2, CB_T, C1, C3 = (
    0, 4, 5, 9, 8, 12, 13, 15, 18, 19, 24, 25, 26, 27, 33, 29)
el = lambda i: mol.GetAtomWithIdx(i).GetSymbol()
assert [el(i) for i in (N_T, N_A, N_G, O_PGA)] == ["N", "N", "N", "O"]
assert mol.GetAtomWithIdx(C1).GetIsAromatic() and mol.GetAtomWithIdx(C3).GetIsAromatic()
assert mol.GetBondBetweenAtoms(32, C1) and mol.GetBondBetweenAtoms(28, C1) and mol.GetBondBetweenAtoms(28, C3)
assert mol.GetBondBetweenAtoms(N_G, 22) and mol.GetBondBetweenAtoms(17, O_PGA)  # lactam N-H; Pga C=O

H = lambda i: [n.GetIdx() for n in mol.GetAtomWithIdx(i).GetNeighbors() if n.GetSymbol() == "H"]
hN_A, hN_T, hN_G = H(N_A)[0], H(N_T)[0], H(N_G)[0]
hA_P, hA_G, hA_T, h1, h3 = H(CA_P)[0], H(CA_G)[0], H(CA_T)[0], H(C1)[0], H(C3)[0]
hB_P, hB_T, hD_P, hOMe = H(CB_P), H(CB_T), H(CD_P), H(OME)

def restraints(meS, meR, hb1P, hb2P):
    """Table S1 ids 1-33 as (groupA, groupB, lower, upper); groups use min distance (r^-6 dominated)."""
    t = [([hN_A], [hN_T], 2.8, .2, .5), ([hN_A], [h1], 3.0, .2, .5), ([hN_A], [hN_G], 5.0, .2, .5),
         ([hN_A], [hA_P], 2.3, .1, .3), ([hN_A], [hb1P], 4.5, .5, .5), ([hN_A], [hb2P], 5.0, .5, .5),
         ([hN_A], meS, 3.0, .5, .5), ([hN_A], meR, 4.0, .5, .5),
         ([hN_T], [hN_A], 2.8, .2, .5), ([hN_T], [h3], 3.0, .2, 1.0), ([hN_T], [hN_G], 4.5, 0, 1.0),
         ([hN_T], [h1], 2.8, .2, .5), ([hN_T], [hB_T[1]], 3.2, .3, .5), ([hN_T], [hB_T[0]], 3.2, .3, .5),
         ([hN_T], meS, 3.8, .2, .5), ([hN_T], meR, 3.8, .2, .5),
         ([h3], [hA_T], 2.8, .2, .5), ([h3], hB_T, 2.7, .3, .5), ([h3], meS, 4.0, .2, .5),
         ([hN_G], [h1], 3.4, .2, .5), ([hN_G], [hA_G], 2.8, .2, .5), ([hN_G], hB_T, 4.5, .3, .5),
         ([hN_G], hOMe, 5.0, 0, 1.0),
         ([h1], [hN_T], 2.8, .2, .5), ([h1], [hN_A], 3.0, .2, .5), ([h1], [hN_G], 3.4, .2, .5),
         ([h1], [hA_P], 3.8, .2, .2), ([h1], meS, 4.0, .2, .5), ([h1], meR, 5.5, .2, .5),
         ([h1], hB_T, 2.7, .3, .5), ([h1], hOMe, 5.0, 0, 1.0),
         ([hA_G], hD_P, 3.0, .5, .5), ([hA_P], meR, 4.5, .2, .5)]
    return [(a, b, d - lo, d + up) for a, b, d, lo, up in t]

ME = [H(ME1), H(ME2)]
SETS = [restraints(ME[i], ME[1 - i], hB_P[j], hB_P[1 - j]) for i in (0, 1) for j in (0, 1)]  # stereo-assignment ambiguity

def gdist(c, a, b):
    return min((c.GetAtomPosition(i) - c.GetAtomPosition(j)).Length() for i in a for j in b)

def score(c):
    best = None
    for k, R in enumerate(SETS):
        v = [max(lo - d, d - hi, 0) for a, b, lo, hi in R for d in [gdist(c, a, b)]]
        s = (sum(x * x for x in v), max(v), sum(x > .3 for x in v), k)
        best = s if best is None or s < best else best
    return best

def hbond(c):
    return (c.GetAtomPosition(hN_T) - c.GetAtomPosition(O_PGA)).Length()

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    p = AllChem.ETKDGv3(); p.randomSeed = 20261015; p.pruneRmsThresh = 0.3
    cids = AllChem.EmbedMultipleConfs(mol, n, p)
    res = FF.MMFFOptimizeMoleculeConfs(mol, maxIters=5000)
    rows = sorted((score(mol.GetConformer(c))[0] + max(0, hbond(mol.GetConformer(c)) - 2.5) ** 2, c)
                  for c in cids)
    print(f"{len(cids)} conformers; best 5 (penalty, cid, E_MMFF, H...O):")
    for s, c in rows[:5]:
        print(f"  {s:7.2f} {c:4d} {res[c][1]:9.2f} {hbond(mol.GetConformer(c)):5.2f}")
    cid = rows[0][1]
    k = score(mol.GetConformer(cid))[3]
    # restrained refinement: flat-bottom restraints on representative atom pairs (closest pair for groups)
    props = FF.MMFFGetMoleculeProperties(mol)
    ff = FF.MMFFGetMoleculeForceField(mol, props, confId=cid)
    conf = mol.GetConformer(cid)
    for a, b, lo, hi in SETS[k]:
        i, j = min(((i, j) for i in a for j in b),
                   key=lambda ij: (conf.GetAtomPosition(ij[0]) - conf.GetAtomPosition(ij[1])).Length())
        ff.MMFFAddDistanceConstraint(i, j, False, lo, hi, 50.0)
    ff.MMFFAddDistanceConstraint(hN_T, O_PGA, False, 1.8, 2.5, 50.0)
    # ideal type II' turn (Pro i+1: phi 60, psi -120; Aib i+2: phi -80, psi 0), +/-30 deg flat bottom
    for (a, b, c_, d), (lo, hi) in [((17, 16, CA_P, 10), (30, 90)), ((16, CA_P, 10, N_A), (-150, -90)),
                                    ((10, N_A, CA_A, 6), (-110, -50)), ((N_A, CA_A, 6, N_T), (-30, 30))]:
        ff.MMFFAddTorsionConstraint(a, b, c_, d, False, lo, hi, 100.0)
    ff.Minimize(maxIts=20000)
    s = score(conf)
    e = FF.MMFFGetMoleculeForceField(mol, props, confId=cid).CalcEnergy()
    print(f"refined cid {cid}: sumsq viol {s[0]:.3f} A^2, max viol {s[1]:.2f} A, >0.3 A: {s[2]}, "
          f"assignment set {k}, H...O {hbond(conf):.2f} A, E_MMFF {e:.2f} kcal/mol")
    out = Chem.Mol(mol, confId=cid)
    m1 = Chem.Mol(mol); m1.RemoveAllConformers(); m1.AddConformer(Chem.Conformer(conf), assignId=True)
    Chem.MolToMolFile(m1, "6a_nmr_restrained_mmff.mol")
    Chem.MolToXYZFile(m1, "6a_nmr_restrained_mmff.xyz")
    print("wrote 6a_nmr_restrained_mmff.{mol,xyz}")
