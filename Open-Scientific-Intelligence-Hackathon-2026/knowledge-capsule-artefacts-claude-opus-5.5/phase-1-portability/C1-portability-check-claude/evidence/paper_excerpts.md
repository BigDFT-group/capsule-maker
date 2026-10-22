# Verbatim excerpts from the paper and SI

Irle, Lazzarini, Hagn, Zacharias & Bach, *Photocatalytic tetrapeptides for enantioselective visible
light-induced transformations*, Nature Synthesis (2026), doi:10.1038/s44160-026-01173-7, CC BY 4.0.

Quoted from the Paper2Agent paper skill `irle2026-tetrapeptide-photocatalysis-paper`
(TengxiangLii/P2A-Robert-2026, commit bc704b2). `paper.md:N` and `supplement.md:N` are line
numbers in its `references/` directory. Markup (`<sup>`, `_`, `**`) is kept as it appears in the skill.

## Experimental target: triplet energy and absorption of 6a

**E1** (`paper.md:33`, Fig. 2 caption)
> Photophysical properties are provided for peptide **6a** and were determined in EtOH solution. From the inflection point (indicated by the dashed blue line) of the phosphorescence spectrum (77 K, EtOH) the triplet energy was calculated as 269 kJ mol<sup>−1</sup>.

**E2** (`paper.md:62`)
> The prominent photophysical characteristics of catalyst **6a** (absorption and luminescence) are due to the thioxanthone embedded in pTxa and are comparable to parent 9_H_-thioxanthen-9-one<sup>36</sup>. The longest wavelength absorption was found at _λ_ = 383 nm (molar decadic absorption coefficient _ε_ = 5,700 M<sup>−1</sup> cm<sup>−1</sup>) and the triplet energy was determined as _E_<sub>T</sub> = 269 kJ mol<sup>−1</sup>.

**E3** (`paper.md:182`, reference 36)
> 36. Nikitas, N. F., Gkizis, P. L. & Kokotos, C. G. Thioxanthone: a powerful photocatalyst for organic reactions. _Org. Biomol. Chem._ **19**, 5237–5253 https://doi.org/10.1039/D1OB00221J (2021).

**E4** (`supplement.md:103`, measurement method)
> **Luminescence spectroscopy** was performed on a _Horiba Scientific_ FluoroMax-4P spectrofluorometer equipped with a continuous Xe source for steady state spectra and a Xe flashlight source for the observation of phosphorescence spectra. Spectra were recorded in _Horiba_ quartz tubes (inner ⌀ = 4 mm) in a small quartz Dewar vessel which was filled with liquid nitrogen (77 K) with a delay of 0.1 ms. Ethanol (_Uvasol_ EtOH, 99.7+%, _Alfa Aesar_) was used as the solvent, and solutions prepared and handled under dry nitrogen atmosphere.

**E5** (paper skill `assets/table/source-data-fig-2.csv`, packaged as `data/source_data_fig2_6a_photophysics.csv`)
Source data of Fig. 2: UV/Vis absorbance (700–200 nm), steady-state emission at rt, and phosphorescence at 77 K (400–650 nm), all normalized. The paper skill documents a source defect: the "Steady state rt" emission column normalizes the wavelength column, not the intensity, so it carries no emission data. The UV/Vis and 77 K phosphorescence columns are unaffected.

## Structure of 6a

**E6** (`paper.md:66`)
> The tetrapeptide adopts a type II’ β-turn conformation<sup>32,37</sup> […] In this βII’ turn the existence of a hydrogen bond between the amide proton of pTxa and the backbone carbonyl of Pga is evident from specific rotating-frame nuclear Overhauser effect restraints (Fig. 3a) between the two residues and a temperature coefficient<sup>40</sup> of −4.7 ppb K<sup>−1</sup> for the amide of pTxa (Supplementary Fig. 8). The photoactive thioxanthone ring is located above the β-turn structure

**E7** (`paper.md:72`, Fig. 3 caption)
> **b**, Structural bundle of **6a** with a heavy atom r.m.s.d. of 0.22 Å indicating a βII’-turn conformation.

**E8** (`supplement.md:181`)
> NMR experiments were conducted at various temperatures ranging from 233 to 298K on a Bruker Avance III NMR spectrometer operating at a 600 MHz proton frequency […] Compound **6a** alone or **6a** and _ent_-**5a** (1:1 molar ratio) were dissolved in _d<sub>2</sub>_-dichloromethane (CD2Cl2, Merck) at a concentration of 10 mM.

**E9** (`supplement.md:183`, restraint bounds)
> ROE distance restraints were extracted from the 2D-ROESY experiment with 200 ms mixing time at 233 K. ROESY cross peak integrals were translated into distance restraints by calibration using the covalently fixed protons in ortho position in the thioxanthone ring system and offset compensation.<sup>[54]</sup> Distances (d) were calculated with the following formula with lower and upper error bounds of 0.2 and 0.5 Å, respectively.

**E10** (`supplement.md:187`)
> Structure calculation was done with Xplor-NIH<sup>[55]</sup> using a standard simulated annealing protocol. […] The final round of structure calculation yielded 90 structures. Amongst these, the 10 best-total-energy structures were used for the calculation of the r.m.s.d. values and for the visualization of the structural bundle.

**E11** (`supplement.md:189–231`, Table S1, packaged as `data/table_s1_noe_restraints.csv`)
33 intramolecular restraints (ids 1–33) with columns Calc. distance, Lower bound and Upper bound, plus two intermolecular restraints (34*, 35*) to _ent_-**5a**:
> \* inter-molecular restraints, hydrogen bonds were defined between the lactame moieties of Pga and _ent_-**5a**.

**E12** (`paper.md:68`, substrate complex)
> In this structure, _ent_-**5a** binds to the lactam ring of Pga in **6a** via two hydrogen bonds, placing the substituents of the allene in a sterically favourable orientation with the _tert_-butyl moiety facing away from the thioxanthone ring, enabling proximity (approximately 4 Å) of the allene and the aromatic ring system of the peptide photocatalyst.

**E13** (`paper.md:106–108`, data availability)
> Primary research data are openly available in the Chemotion Repository at https://doi.org/10.14272/collection/RMI_2026-01-30. Source data are provided with this paper.

No PDB or BMRB entry and no coordinate file is cited. The Chemotion 6a molecule record
(doi:10.14272/WQGGCBKETYIIRM-BHIFYINESA-N.2) gives the SMILES and InChI and is packaged as
`data/6a_chemotion_molecule_record.csv`.
