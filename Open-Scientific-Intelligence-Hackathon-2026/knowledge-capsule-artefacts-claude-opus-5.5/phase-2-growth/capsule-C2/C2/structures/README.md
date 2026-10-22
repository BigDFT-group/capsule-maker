# 3D structures of tetrapeptide catalyst 6a

6a = (*R*,*R*,*S*)-Pga-Pro-Aib-pTxa-OMe, C31H34N4O7S, 77 atoms, neutral, closed-shell singlet.

The authors deposited no coordinates: no PDB entry, and Chemotion holds only spectra. These structures are rebuilt from published data:

- **Connectivity and stereochemistry**: Chemotion molecule [10.14272/WQGGCBKETYIIRM-BHIFYINESA-N.2](https://doi.org/10.14272/WQGGCBKETYIIRM-BHIFYINESA-N.2).
- **Conformation**: the 33 intramolecular ROE distance restraints of Table S1 (2D-ROESY, 233 K, CD2Cl2), plus the type II′ β-turn reported in the paper (Fig. 3b): the pTxa NH···O=C Pga hydrogen bond and ideal turn torsions.

| File | Method | Max NOE violation | Notes |
|---|---|---|---|
| `6a_nmr_gfn2_ch2cl2_restrained.xyz/.mol` | **recommended.** GFN2-xTB/ALPB(CH2Cl2), flat-bottom NOE restraints | 0.07 Å | turn φ/ψ Pro 56/−126, Aib −81/1; NH···O 2.02 Å |
| `6a_nmr_restrained_mmff.xyz/.mol` | best of 569 ETKDG conformers, MMFF94 with NOE and turn-torsion restraints | 0.24 Å | starting geometry for the xTB runs |
| `6a_nmr_gfn2_ch2cl2.xyz/.mol` | unrestrained GFN2-xTB/ALPB(CH2Cl2) relaxation from the MMFF structure | 1.40 Å (8 > 0.3 Å) | turn kept; pTxa side chain rotated (χ1 −61°). This is the nearest local minimum, 0.49 eV (11.4 kcal/mol) below the restrained structure |

Atom order is identical in all files: SMILES heavy-atom order, then hydrogens. Indices are 0-based (add 1 for 1-based programs). The thioxanthone is atoms 28–42, with S at 38 and O at 35 (C9=O, carbonyl C at 34). pTxa Cβ (27) is bonded to ring position C2 (28); C1 is 33.

Reproduce (needs `uv`):

```bash
uv run --with rdkit python build_6a.py 600                          # MMFF, NOE-restrained
uv run --with tblite --with ase --with rdkit python relax_xtb.py    # xTB restrained; add --free for unrestrained
```

## For excitation calculations

- The low-lying states are localised on the 2-alkyl-thioxanthone. Before TDDFT, re-optimise at your DFT level, ideally keeping the NOE restraints or freezing the backbone dihedrals, because a free optimisation drifts out of the NMR conformation as the xTB run did.
- The experimental reference values are for 6a in EtOH (main text, Fig. 2):
  - longest-wavelength absorption at λ = 383 nm (3.24 eV), ε = 5,700 M⁻¹ cm⁻¹
  - E_T = 269 kJ mol⁻¹ (2.79 eV), from 77 K phosphorescence
- The NMR conformation was determined in CD2Cl2 at 233 K. The reactions run in CH2Cl2 at −70 °C, and the photophysics were measured in EtOH.
- The NMR structure is a restraint-averaged model: the authors' bundle had a 0.22 Å heavy-atom r.m.s.d. Consider several conformers, for example from `build_6a.py` with other seeds, when comparing spectra.
