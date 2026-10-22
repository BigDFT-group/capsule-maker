# Research Capsule

Phase 2 of reproducing E_T(6a) = 269 kJ/mol with BigDFT Delta-SCF on TSUBAME4.0: grid-converged PBE vertical gap, converged T1 SCF protocol, constrained (thioxanthone-only) PBE adiabatic E_T; PBE0 single points queued as the next step

Origin: local-json — Curated by the agent from this session's TSUBAME4.0 Phase 2 runs (logs, dry runs, job record) and the researcher's decisions of 2026-10-22; provenance classes [TOOL]/[RESEARCHER]/[AI]

## Knowledge

### cor-index (correction, verified)

[TOOL] Thioxanthone atoms are 0-based indices 28-42 (1-based 29-43): S 38, O 35, carbonyl C 34; pTxa C-beta 27 bonded to ring C2 (28); ring C1 is 33. Identical in S1, S2 and S3 (43 heavy atoms first, then 34 H).

Evidence: ev-structures, ev-runlog
Provenance: session-structures, session-curation
Supersedes: res-index-old

### cor-p2-t1-scf (correction, verified)

[TOOL] 6a T1 needs dft itermax 200 and nrepmax 5: all 12 T1 reruns converged below 1e-5 after 490-560 SCF iterations (15 min to 1 h 37 min on 20 MPI x 4 OMP), magnetisation 2.000. All later T1 inputs carry these settings.

Evidence: ev-p2-energies
Provenance: session-phase2
Supersedes: fail-p2-t1-itermax

### cor-strain (correction, verified)

[TOOL, curation] The 0.49 eV figure used the penalty-inclusive energy. The GFN2 electronic difference S1 - S3 is 0.453 eV (10.4 kcal/mol): -3464.6577 vs -3465.1108 eV from the per-atom energy columns. structures/README.md is packaged unchanged and still says 0.49 eV.

Evidence: ev-structures, ev-runlog
Provenance: session-curation
Supersedes: res-strain-old

### cor-turn (correction, verified)

[AI decision] Because the paper reports a type II' turn and Aib phi = -162 deg is far from ideal (-80), ideal II' torsion windows (Pro 60/-120, Aib -80/0, +/-30 deg) were added to the MMFF refinement.

Evidence: ev-runlog
Provenance: session-structures
Supersedes: res-mmff-v1

### ctx-env (context, verified)

[TOOL] Compute environment for the BigDFT runs: BigDFT module build with libbigdft 1.9.5, PSolver 1.10, futile 1.9, libxc 4.3.4 (hybrids such as PBE0 available), CHESS 0.2.4, OpenMPI 5.0.7; Slurm CPU cluster, AMD EPYC 7713 (Zen3), 64-128 cores per node, no GPUs. The BigDFT module does not provide PyBigDFT; PyBigDFT 1.9.6 is available on the cluster in a user conda environment and locally. bigdft-tool needs a 'python' on PATH and BIGDFT_ROOT pointing at the BigDFT bin directory.

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### ctx-p2-disk (context, verified)

[TOOL] TSUBAME storage: /work counts against the 125 GB home quota; output: {orbitals: binary} writes 6-12 GB per 6a state, about two thirds of it atomic-orbital files not needed for restarts. Superfluous files were moved to a group disk; plan disk before chaining wavefunction restarts.

Evidence: ev-p2-runs
Provenance: session-phase2
Supersedes: none

### ctx-p2-request (context, verified)

[RESEARCHER, 2026-10-22] Phase 2 request: run the 24 dry-run-validated PBE grid-convergence inputs on 6a S1 (S0 and T1), then PBE0 single points on 6a, and compare with the endorsed 2.79 +/- 0.15 eV; run the calculations on TSUBAME4.0. Later: keep the jobs running as they are and capsulize the Phase 2 state.

Evidence: ev-p2-runs
Provenance: researcher-phase2
Supersedes: none

### ctx-p2-tsubame (context, verified)

[TOOL] Phase 2 ran on TSUBAME4.0 (AMD EPYC 9654 nodes, Altair Grid Engine, 24 h job limit) with a user-built BigDFT (libbigdft 1.9.5, PSolver 1.10, futile 1.9, CHESS 0.2.4, libxc 4.3.4; GCC + OpenMPI 5.0.7), identical library versions to ctx-env; PyBigDFT 1.9.6 in conda. Modules cuda/12.8.0, openmpi/5.0.7-gcc, intel/2025.0.0, UCX LD_PRELOAD, OMPI_MCA_coll=^hcoll (scripts/bigdft_env.sh). Launch: mpirun -np N --map-by slot:PE=OMP (fail-srun lesson). PBE runs: cpu_80 (80 cores, 184 GB) as 20 MPI x 4 OMP; PBE0: node_f (192 cores, 768 GB) as 24 MPI x 8 OMP. GPUs unused.

Evidence: ev-p2-runs
Provenance: session-phase2, tsubame4-runs
Supersedes: none

### ctx-p2a (context, verified)

[TOOL] The paper has no code repository, so Paper2Agent produced a paper-only skill (no MCP server); it was used for reading and searching the paper and SI. Structures were computed with RDKit, ASE and tblite via uv.

Evidence: ev-paper, ev-runlog
Provenance: paper-skill, session-structures
Supersedes: none

### ctx-paper (context, verified)

[PAPER] 6a = (R,R,S)-Pga-Pro-Aib-pTxa-OMe, C31H34N4O7S, <750 Da. N-terminal pyroglutamic acid binds lactam substrates by two H-bonds; the C-terminal pTxa thioxanthone absorbs visible light and sensitises by triplet energy transfer. NMR (33 ROE restraints, 233 K, CD2Cl2, Xplor-NIH; 10-structure bundle, heavy-atom r.m.s.d. 0.22 A) gives a type II' beta-turn with a pTxa NH...O=C Pga H-bond and the thioxanthone above the turn.

Evidence: ev-paper
Provenance: paper, si, paper-skill
Supersedes: none

### ctx-phos-data (context, verified)

[PAPER] Fig. 2 source data are packaged: UV/Vis (700-200 nm) and 77 K phosphorescence (400-650 nm), both normalized. The 'Steady state rt' emission column is a source defect (it normalizes the wavelength column) and carries no emission data. The phosphorescence curve permits an independent re-derivation of the onset energy.

Evidence: ev-paper
Provenance: paper, paper-skill
Supersedes: none

### ctx-request (context, verified)

[RESEARCHER] Objective of this capsule: reproduce the experimental triplet energy E_T = 269 kJ/mol of catalyst 6a with BigDFT, starting from the agentified paper (Paper2Agent skill), the BigDFT agent skills and Capsule-Maker. Earlier questions that produced the structures: whether the authors give optical excitation energies, and obtaining 6a 'in a position good for the simulation of excitation'.

Evidence: ev-runlog
Provenance: researcher-request, session-structures
Supersedes: none

### ctx-target (context, verified)

[PAPER] Experimental target: E_T(6a) = 269 kJ/mol, from the inflection point of the 77 K phosphorescence spectrum in EtOH (Fig. 2, main text; FluoroMax-4P, 0.1 ms delay). Longest-wavelength absorption 383 nm, epsilon 5,700 M-1 cm-1 (EtOH). The paper attributes both to the thioxanthone in pTxa and calls them comparable to parent 9H-thioxanthen-9-one (ref. 36, Nikitas et al., Org. Biomol. Chem. 19, 5237 (2021)). The paper gives no photophysical data for other catalysts or substrates. [AI conversion] 269 kJ/mol = 2.788 eV; 383 nm = 3.24 eV.

Evidence: ev-paper
Provenance: paper, si, paper-skill
Supersedes: none

### dec-bounds (decision, verified)

[PAPER-supported AI interpretation] Table S1 'Lower/Upper bound' columns are deviations from the calculated distance: bounds = d_calc - lower and d_calc + upper (SI: 'lower and upper error bounds of 0.2 and 0.5 A').

Evidence: ev-paper
Provenance: si, session-structures
Supersedes: none

### dec-calibration (decision, superseded)

[AI proposal] Use parent 9H-thioxanthen-9-one as a calibration system for the BigDFT triplet protocol, because the paper calls the photophysics of 6a comparable to it (ref. 36). Its experimental E_T must be retrieved from the literature (ref. 36 or primary data), not recalled. Awaits the researcher's endorsement.

Evidence: ev-paper
Provenance: session-curation
Supersedes: none

### dec-calibration-ok (decision, verified)

[RESEARCHER, 2026-10-20] Confirmed: calibrate the Delta-SCF triplet protocol on parent thioxanthone before 6a.

Evidence: ev-paper
Provenance: researcher-request
Supersedes: dec-calibration

### dec-criteria (decision, superseded)

[AI, from the study plan; not explicitly endorsed] Pre-registered criteria: the calibration on thioxanthone passes if the protocol is within 0.2 eV of the literature E_T; 6a counts as reproduced if the PBE0 adiabatic Delta-SCF E_T is within +/-0.15 eV (+/-15 kJ/mol) of 2.79 eV. All levels are reported; nothing is tuned toward 269 kJ/mol.

Evidence: none
Provenance: session-curation
Supersedes: none

### dec-criteria-ok (decision, verified)

[RESEARCHER, 2026-10-20] Endorsed: calibration passes within 0.2 eV of the literature E_T of thioxanthone; 6a is reproduced if the PBE0 adiabatic Delta-SCF E_T is within +/-0.15 eV of 2.79 eV.

Evidence: ev-runlog
Provenance: researcher-request
Supersedes: dec-criteria

### dec-dryrun-first (decision, verified)

[RESEARCHER, 2026-10-20] Every BigDFT input must first pass a dry run (PyBigDFT SystemCalculator(dry_run=True), i.e. bigdft-tool memory estimation without SCF). If any input gives an error, no calculation is performed.

Evidence: ev-runlog
Provenance: researcher-request
Supersedes: none

### dec-p2-geopt-constrained (decision, verified)

[RESEARCHER, 2026-10-22] Switch the main path to option A: relax only the thioxanthone (0-based atoms 28-42 plus its 7 H, 70-76; C2 ring position bonded to pTxa C-beta 27) with the other 55 atoms frozen at S1, in both S0 and T1; keep the free runs as a sensitivity check. Reasons discussed: dec-select warns that free DFT relaxation leaves the NMR conformation, and E_T is measured in a 77 K glass. The free T1 run was later cancelled at the researcher's request.

Evidence: ev-p2-runs
Provenance: researcher-phase2
Supersedes: dec-p2-geopt-free

### dec-p2-geopt-free (decision, superseded)

[RESEARCHER, 2026-10-22] For the adiabatic E_T, optimise 6a S0 and T1 with fully free PBE geometry optimisations from S1 (chosen over a backbone-constrained or vertical-only approach).

Evidence: ev-p2-runs
Provenance: researcher-phase2
Supersedes: none

### dec-p2-grid (decision, verified)

[AI decision, evidence-backed] Use hgrid 0.35 bohr, rmult (6,9) for all 6a production runs. res-p2-grid shows the triplet gap converged to < 1 meV there, which also verifies the provisional thioxanthone grid of dec-tx-grid (same settings), so the calibration and 6a share one converged grid.

Evidence: ev-p2-energies
Provenance: session-phase2
Supersedes: dec-tx-grid

### dec-psp (decision, superseded)

[AI proposal, awaiting the researcher's endorsement] Use the Goedecker-Krack PBE HGH-K pseudopotentials (PyBigDFT Database/psppar/Krack/PBE, XC 11) for all elements: C 4, H 1, N 5, O 6, S 6 valence electrons, giving 226 electrons (113 doubly occupied orbitals) for 6a and 72 (36) for thioxanthone. Reason: one consistent family; the HGH-K+NLCC 'SS' set lacks S. The same PBE pseudopotentials would be used for PBE0, a standard approximation.

Evidence: ev-runlog, ev-structures
Provenance: session-curation
Supersedes: none

### dec-psp-ok (decision, verified)

[RESEARCHER, 2026-10-20] Confirmed: Goedecker-Krack PBE HGH-K pseudopotentials for C, H, N, O and S (226 electrons for 6a, 72 for thioxanthone).

Evidence: ev-structures
Provenance: researcher-request
Supersedes: dec-psp

### dec-rebuild (decision, verified)

[TOOL+AI] The authors deposited no coordinates (no PDB/BMRB; Chemotion has SMILES/spectra only), so 6a was rebuilt from the Chemotion SMILES and fitted to Table S1 restraints 1-33 plus the reported type II' turn.

Evidence: ev-paper, ev-runlog
Provenance: session-structures, chemotion-6a, si
Supersedes: none

### dec-select (decision, superseded)

[AI recommendation, not yet confirmed by the researcher] Use S1 as the starting geometry for excitation and triplet calculations: the only structure satisfying all Table S1 restraints and the II' turn at an electronic-structure level. Use S3 as a sensitivity check for chromophore placement; S2 is a force-field intermediate. A free DFT re-optimisation would drift out of the NMR conformation as S3 did, so freeze or restrain the backbone.

Evidence: ev-structures
Provenance: session-structures
Supersedes: none

### dec-select-ok (decision, verified)

[RESEARCHER, 2026-10-20] Confirmed: S1 is the starting geometry for the triplet calculations; S3 serves as the sensitivity check for chromophore placement.

Evidence: ev-structures
Provenance: researcher-request
Supersedes: dec-select

### dec-state (decision, verified)

[AI] 6a is treated as an isolated neutral closed-shell singlet (charge 0, 77 atoms, all 34 H explicit); coordinates in Angstrom.

Evidence: ev-structures
Provenance: session-structures
Supersedes: none

### dec-tx-grid (decision, superseded)

[AI choice] Thioxanthone geometry optimisations use hgrid 0.35 bohr and rmult (6, 9), chosen as a conservative grid before the 6a convergence study; it is to be checked against that study.

Evidence: none
Provenance: session-curation
Supersedes: none

### ev-lit-tx (evidence, verified)

[LITERATURE] Quoted excerpts and references for the thioxanthone triplet energy, with what could not be retrieved (paper ref. 36, primary 1971/1974 measurements).

Evidence: none
Provenance: jbcs2010, session-curation
Supersedes: none

### ev-p2-dryruns (evidence, verified)

[TOOL] bigdft-tool memory-estimation results of all Phase 2 dry runs (54 entries).

Evidence: none
Provenance: session-phase2
Supersedes: none

### ev-p2-energies (evidence, verified)

[TOOL] Condensed numbers from every Phase 2 BigDFT log (final energies, SCF iterations, gnrm, magnetisation, MPI/OMP, geopt forces) with each full log's SHA-256, plus the E_T summary and both grid-study tables; full logs in the external archive.

Evidence: none
Provenance: session-phase2
Supersedes: none

### ev-p2-geometries (evidence, verified)

[TOOL] Plain XYZ (A) of the PBE constrained S0/T1 minima and the free S0 minimum, extracted from the BigDFT final_*.yaml files by analysis/collect_evidence.py; same atom order as C1 bigdft/6a_S1.xyz.

Evidence: none
Provenance: session-phase2
Supersedes: none

### ev-p2-runs (evidence, verified)

[TOOL] TSUBAME job record of Phase 2 (job IDs, resources, outcomes, cancellations) and the exact inputs of every stage.

Evidence: none
Provenance: session-phase2
Supersedes: none

### ev-paper (evidence, verified)

[PAPER] Verbatim excerpts E1-E13 of the paper and SI from the paper skill (with line numbers): E_T 269 kJ/mol from the 77 K EtOH phosphorescence inflection point, 383 nm absorption, comparison with parent thioxanthone (ref. 36), luminescence method, NMR conditions, restraint bounds, Xplor-NIH bundle, type II' turn, substrate complex, data availability. Table S1, the Chemotion 6a record and the Fig. 2 source data are packaged as CSV.

Evidence: none
Provenance: paper, si, chemotion-6a, paper-skill
Supersedes: none

### ev-phase1 (evidence, verified)

[TOOL] Packaged Phase 1 runs: inputs as run, BigDFT logs (install prefix redacted), geopt.mon, final geometries, timing files, Slurm outputs, and phase1_summary.json from procedures/analyze_phase1.py (stdlib).

Evidence: none
Provenance: session-curation
Supersedes: none

### ev-runlog (evidence, verified)

[TOOL] Chronological run log (42 steps) of the structure construction with tool-call IDs, commands, printed metrics and outcomes, plus the two BFGS logs of the GFN2-xTB relaxations; steps 19-42 re-derived or run at curation.

Evidence: none
Provenance: session-structures, session-curation
Supersedes: none

### ev-structures (evidence, verified)

[TOOL] The three 6a geometries (S1, S2, S3) as XYZ and MOL with their generating scripts; SHA-256, composition C31H34N4O7S, thioxanthone indices and the S1-S3 energy difference are checked by tests/test_structures.py plus the BigDFT-ready plain XYZ copies and the thioxanthone geometry (stdlib, 21 tests, passing at curation).

Evidence: none
Provenance: session-structures, session-curation
Supersedes: none

### fail-dryrun-env (failed_attempt, verified)

[TOOL] The first dry-run attempts failed for environment reasons, not input errors: PyBigDFT rejects an absolute run_dir ('must be a sub-directory'), and bigdft-tool (#!/usr/bin/env python) found no python on the cluster PATH. Fixed by a relative run_dir in dry_run.py and by putting the conda env with PyBigDFT first on PATH; BIGDFT_ROOT must be the BigDFT bin directory.

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### fail-hookean (failed_attempt, verified)

[TOOL] Restraining xTB with ASE Hookean springs at the Table S1 upper bounds (k 5) failed: max violation 1.49 A, 6 > 0.3 A, all too SHORT (ids 5, 6, 11, 13, 15, 22), because Hookean acts only above rt and cannot enforce lower bounds. Replaced by a two-sided FlatBottom constraint. Do not reuse Hookean for this.

Evidence: ev-runlog
Provenance: session-structures
Supersedes: none

### fail-p2-restart-displaced (failed_attempt, verified)

[TOOL] Restarting from S1 wavefunctions at the constrained T1 minimum (max displacement 0.56 A) gives a poor guess (iteration 1: -337.7 Ha, gnrm 0.78), no better than an input guess. Hence stage 06 recomputes PBE wavefunctions at the exact target geometries before the PBE0 restart.

Evidence: ev-p2-runs
Provenance: session-phase2
Supersedes: none

### fail-p2-t1-itermax (failed_attempt, superseded)

[TOOL] With BigDFT defaults (itermax 50, nrepmax 1) all 12 T1 single points at S1 stopped unconverged (gnrm 6.6e-5 to 1.5e-4 > gnrm_cv 1e-5) while S0 converged in 23-25 iterations. The resulting vertical gap 2.547 eV was 35 meV too high; T1 energies were still falling by up to 37 meV.

Evidence: ev-p2-energies
Provenance: session-phase2
Supersedes: none

### fail-pbe0-oom (failed_attempt, verified)

[TOOL] First PBE0 submission (4 thioxanthone single points, 16 MPI x 2 OMP, 24 GB per job) was OOM-killed after about 8 min, in the input guess and before the first SCF iteration; MaxRSS 23-25 GB per job, no results. BigDFT's own estimate was 501 MB per process (about 8 GB per job): the dry-run memory estimate does not include exact-exchange memory, so a dry run validates hybrid inputs but not their memory. PBE0 memory must be measured before sizing jobs.

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### fail-psp-api (failed_attempt, verified)

[TOOL] PyBigDFT 1.9.6 Inputfile.set_psp_krack('PBE', elements=[...]) and set_psp_nlcc(elements=[...]) silently load nothing: set_psp_directory matches psp.endswith(element), but the files are named psppar.X.yaml. Workaround: set_psp_file(filename='.../psppar.X.yaml', element='X') per element, then check that every psppar.X key is present and the electron count is 226 (6a) or 72 (thioxanthone).

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### fail-srun (failed_attempt, verified)

[TOOL] Launching BigDFT with srun on this cluster fails: OpenMPI 5 needs PMIx, Slurm offers only pmi2, so srun starts N independent single-process copies ('12 singletons'), which overwrite each other's logs and run out of memory (first Phase 1 submission, cancelled after 42 s, no results). Use mpirun -np $SLURM_NTASKS --map-by slot:PE=$OMP_NUM_THREADS inside the Slurm allocation, and check 'Number of MPI tasks' in the log at start-up.

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### hyp-group-min (hypothesis, hypothesis)

[AI] Methyl and CH2 groups are treated by the minimum distance over group members (r^-6 dominated); the unreported pro-S/pro-R methyl and Pro H-beta assignments are resolved by taking the best of 4 assignment sets (set 1 chosen). The authors' Xplor-NIH averaging may differ.

Evidence: ev-runlog
Provenance: session-structures
Supersedes: none

### hyp-p2-t1-frontier (hypothesis, hypothesis)

[AI interpretation] Slow T1 convergence: the highest occupied spin-down levels are closely spaced (-0.192, -0.201, -0.202, -0.209 Ha in the first T1 run), probably peptide amide/carbonyl lone pairs that PBE places near the thioxanthone levels, so the triplet hole can move between them. Not yet tested by spin-density or orbital analysis.

Evidence: ev-p2-energies
Provenance: session-phase2
Supersedes: none

### hyp-pbe-underestimate (hypothesis, superseded)

[AI interpretation, untested] The PBE deficit is attributed to the semilocal functional (self-interaction error lowers the open-shell triplet); the planned PBE0 single points at the PBE S0/T1 geometries should raise E_T. Other contributions (grid, zero-point energy, solvent, the literature value being an onset or 0-0 energy) are not yet separated.

Evidence: none
Provenance: session-curation
Supersedes: none

### proc-generation (procedure, verified)

[TOOL] build_6a.py: RDKit ETKDGv3 (seed 20261015, 600 attempts, prune 0.3 A) -> MMFF94 -> score vs Table S1 + turn H-bond -> best conformer refined with flat-bottom MMFF distance restraints (k 50), H-bond 1.8-2.5 A and II' torsion windows -> S2. relax_xtb.py: GFN2-xTB/ALPB(CH2Cl2), ASE BFGS fmax 0.02 eV/A; default mode applies FlatBottom restraints (k 2.5 eV/A^2) -> S1; '--free' -> unrestrained (S3 was made by an earlier version without restraint code that ran the same calculation). Versions: rdkit 2026.9.1, tblite 0.7.0, ase 3.29.0.

Evidence: ev-runlog, ev-structures
Provenance: session-structures
Supersedes: none

### proc-inputs (procedure, verified)

[TOOL] procedures/make_inputs.py (PyBigDFT 1.9.6) writes 26 self-contained YAML inputs (dft + geopt + embedded Angstrom posinp + psppar from bigdft/psppar via set_psp_file) and index.json. Common: ixc PBE, free boundary conditions, gnrm_cv 1e-5. T1 = spin_polarize(mpol=2) -> nspin 2, mpol 2. Phase 1: tx_S0/T1_pbe_geopt, hgrid 0.35 bohr, rmult (6, 9), SQNM, 300 steps, betax 1.0, forcemax 2e-4 Ha/bohr. Phase 2: 6a S1 S0/T1 single points at hgrid 0.45/0.40/0.35/0.30 x rmult (5,8)/(6,9)/(7,10). Phase 1b: thioxanthone PBE0 single points tx_{S0,T1}_pbe0_at_{S0,T1}pbe at the converged PBE geometries (hgrid 0.35, rmult (6, 9)). Output is deterministic (regenerated byte-identical). procedures/dry_run.py runs SystemCalculator(dry_run=True) on a directory of inputs and writes a summary; procedures/run_bigdft.slurm runs one input (mpirun -np $SLURM_NTASKS --map-by slot:PE=$OMP_NUM_THREADS bigdft -n NAME).

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### proc-p2-restart (procedure, verified)

[TOOL] Wavefunction restart: write with output: {orbitals: binary}, then copy the whole data-<src> directory (glr.dat, wavefunction.yaml, wavefunction-*.bin) to data-<name> and set dft inputpsiid: 2. At an unchanged geometry the restart converges in 2 iterations to the same energy (2e-9 Ha). Copying only the wavefunction files fails (glr.dat missing). Atomic-orbital files are not needed.

Evidence: ev-p2-runs
Provenance: session-phase2
Supersedes: none

### proc-p2-workflow (procedure, verified)

[TOOL] Stage pipeline (phase2/inputs): 01 T1 reruns; 02 PBE at S1 writing wavefunctions; 03 PBE0 at S1 (restart from 02); 04 free SQNM geopt; 05 constrained SQNM geopt (Frozen: fxyz on 55 atoms, restart from 02); 06 PBE at the constrained minima writing wavefunctions; 07 PBE0 at the constrained minima (restart from 06). Geopt settings as the thioxanthone protocol (SQNM, 300 steps, betax 1.0, forcemax 2e-4, frac_fluct 1.0). Grid Engine array jobs via scripts/run_array*.sh; every input passes scripts/dryrun_dir.sh first; analysis/collect_evidence.py condenses logs into the evidence files; tests/test_phase2_evidence.py checks them.

Evidence: ev-p2-runs, ev-p2-energies
Provenance: session-phase2
Supersedes: none

### q-complex (question, unresolved)

The catalyst-substrate complex 6a.ent-5a (Table S1 intermolecular ids 34-35; allene ~4 A from the thioxanthone) has not been built.

Evidence: ev-paper
Provenance: session-structures, si
Supersedes: none

### q-conditions (question, unresolved)

Conditions differ: NMR in CD2Cl2 at 233 K, E_T and absorption in EtOH (E_T in a 77 K glass), reactions in CH2Cl2 at -70 C. The authors' restraint averaging and stereo-assignments are not reported.

Evidence: ev-paper
Provenance: session-structures
Supersedes: none

### q-ensemble (question, unresolved)

A single conformer stands in for the NMR ensemble (authors' bundle r.m.s.d. 0.22 A, 10 of 90 structures). Sensitivity of excitation energies to conformation is unknown; other seeds of build_6a.py can supply more restraint-compatible conformers.

Evidence: ev-paper
Provenance: session-structures
Supersedes: none

### q-hybrid-psp (question, unresolved)

Effect of using PBE-generated pseudopotentials with PBE0 on the triplet energy is not quantified.

Evidence: none
Provenance: session-curation
Supersedes: none

### q-p2-absorption (question, unresolved)

PBE T1@cgS0 (vertical absorption partner, stage 06) and T1@cgT1 single point with wavefunctions were still running when C2 was made.

Evidence: ev-p2-runs
Provenance: session-phase2
Supersedes: none

### q-p2-pbe0 (question, unresolved)

Next action and open criterion: PBE0 single points at the constrained minima (stage 07: S0@cgS0, T1@cgT1, T1@cgS0, S0@cgT1; job 9102503) and at S1 (stage 03; job 9100870) were queued, not finished, when C2 was made. The endorsed test is PBE0 adiabatic E(T1@cgT1) - E(S0@cgS0) within 2.79 +/- 0.15 eV. If PBE0 shifts 6a as it shifted thioxanthone (+0.25 eV), E_T would be near 2.6 eV, at the lower edge; this is an extrapolation, not a result.

Evidence: ev-p2-runs
Provenance: session-phase2
Supersedes: none

### q-pbe0-geometry (question, unresolved)

PBE0 energies were evaluated at PBE geometries, not PBE0-optimised ones; the effect on the adiabatic E_T is not quantified.

Evidence: none
Provenance: session-curation
Supersedes: none

### q-t1-character (question, unresolved)

The character of the computed thioxanthone T1 (pi-pi* vs n-pi*) is not determined: no spin density or orbital analysis yet. The 0.051 A C9=O elongation shows carbonyl involvement but does not decide it.

Evidence: none
Provenance: session-curation
Supersedes: none

### q-tx-lit (question, unresolved)

Partly answered by res-tx-lit (secondary source, 274.1 kJ/mol). Still open: the primary measurement (Dalton & Turro 1971; Dalton & Montgomery 1974) and paper ref. 36 were not accessed, so the method, temperature and whether the value is a 0-0 or an onset energy are unconfirmed.

Evidence: ev-paper
Provenance: session-curation
Supersedes: none

### q-versions (question, unresolved)

Library versions were not pinned at run time; rdkit/tblite/ase versions were recovered from the uv cache, numpy and Python versions are unknown. Exact ETKDG reproduction is version- and platform-dependent.

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### q-zpe (question, unresolved)

Zero-point and vibronic corrections are not computed; the Delta-SCF values are electronic adiabatic energies, while experiment reports the phosphorescence onset / inflection point.

Evidence: none
Provenance: session-curation
Supersedes: none

### res-dryrun (result, verified)

[TOOL] Dry run of all 26 inputs on the cluster (bigdft-tool memory estimation, no SCF): 26/26 passed, no errors. Electrons 226 (6a) / 72 (thioxanthone). T1 inputs are read as collinear nspin 2, mpol 2, all orbitals singly occupied. Pseudopotentials come from the given files. Serial memory-peak estimates: 6a S0 4.4 (h0.45 r5-8) to 24.1 GB (h0.30 r7-10), T1 8.8-47.9 GB; thioxanthone S0 2.0 GB, T1 4.0 GB. Grids from 84x72x79 to 146x128x139 points. The up/down orbital split is not printed in a dry run and must be checked in the first real log.

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### res-dryrun-pbe0 (result, verified)

[TOOL] Dry run of the 4 thioxanthone PBE0 inputs: 4/4 passed, 72 electrons; read as ixc -406 'PBEH (PBE0)', exact exchange parallelised with OP2P; serial memory estimates 2.0 GB (S0) and 4.0 GB (T1). The only warning is 'PSP generated with a different XC' (PBE pseudopotentials with PBE0). No errors.

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### res-format (result, verified)

[TOOL] S1 and S3 .xyz are 9-column extended XYZ (element, x, y, z, per-atom energy, 3 forces, charge); S2 .xyz is plain 4-column. Strict readers (e.g. BigDFT) need the extra columns stripped; the .mol files carry the same coordinates with bonds.

Evidence: ev-structures
Provenance: session-curation
Supersedes: none

### res-functional-effect (result, verified)

[TOOL] At identical PBE geometries, PBE0 raises the adiabatic E_T of thioxanthone by 24.05 kJ/mol (0.249 eV) relative to PBE (236.70 -> 260.75 kJ/mol), supporting the hypothesis that the PBE deficit is mainly due to the functional. Grid, zero-point, solvent and PBE0-geometry effects remain unseparated.

Evidence: ev-phase1
Provenance: session-curation
Supersedes: hyp-pbe-underestimate

### res-index-old (result, superseded)

[TOOL] First README draft: thioxanthone = C28-C45, S43.

Evidence: ev-runlog
Provenance: session-structures
Supersedes: none

### res-mmff-v1 (result, superseded)

[TOOL] First MMFF refinement (cid 82 of 569): max violation 0.22 A, H...O 2.38 A, but Aib phi/psi -162/29, not a type II' turn.

Evidence: ev-runlog
Provenance: session-structures
Supersedes: none

### res-p2-cgeopt (result, verified)

[TOOL] Constrained PBE minima (option A): S0 converged in 68 SQNM steps, T1 in 94 (Fmax 3.4e-4 and 3.8e-4 Ha/bohr, below the force noise 5.0e-4 and 8.9e-4; stop by frac_fluct, as in Phase 1). Only atoms 28-42 and 70-76 moved (max 0.29 A in S0, 0.56 A in T1). C34=O35 1.240 A (S0) and 1.288 A (T1), cf. thioxanthone 1.236 -> 1.287 A. Relaxation energies from S1: S0 -0.159 eV, T1 -0.318 eV (part of each is the GFN2 -> PBE geometry change).

Evidence: ev-p2-energies, ev-p2-geometries
Provenance: session-phase2
Supersedes: none

### res-p2-dryrun (result, verified)

[TOOL] dec-dryrun-first honoured on TSUBAME: bigdft-tool memory estimation passed for the 24 C1 Phase 2 inputs and for all 30 new inputs (stages 01-07, incl. the superseded cold-start PBE0 pair); 226 electrons each, no BigDFT error block. PBE0 inputs read as ixc -406 with only the expected 'PSP generated with a different XC' warning. Estimated peaks (16 processes) 0.85-4.4 GB per process; not valid for exact-exchange memory.

Evidence: ev-p2-dryruns
Provenance: session-phase2
Supersedes: none

### res-p2-free-s0 (result, verified)

[TOOL] Free PBE S0 geopt from S1 converged in 86 steps (Fmax 3.3e-4) at -358.886769 Ha, 0.42 eV below the constrained S0 minimum: the unconstrained peptide relaxes away from the NMR-fitted conformation, as S3 did with GFN2-xTB.

Evidence: ev-p2-energies, ev-p2-geometries
Provenance: session-phase2
Supersedes: none

### res-p2-free-t1-partial (result, unverified)

[TOOL] Free PBE T1 geopt was cancelled after ~108 steps (Fmax ~2e-3, not converged) at -358.800552 Ha; with the free S0 minimum this gives a provisional 2.346 eV, close to the constrained 2.353 eV, suggesting the peptide conformation affects E_T little. Not a converged result.

Evidence: ev-p2-energies
Provenance: session-phase2
Supersedes: none

### res-p2-grid (result, verified)

[TOOL] PBE vertical Delta-SCF gap of 6a at S1 (converged T1): 2.5114-2.5126 eV over hgrid 0.45/0.40/0.35/0.30 x rmult (5,8)/(6,9)/(7,10), a 1.2 meV spread; 2.5120 eV = 242.37 kJ/mol at hgrid 0.35, rmult (6,9), 0.4 meV from the finest grid. Absolute S0 energies change by 0.1 Ha over the same range; the gap does not.

Evidence: ev-p2-energies
Provenance: session-phase2
Supersedes: none

### res-p2-pbe-adiabatic (result, verified)

[TOOL] PBE adiabatic Delta-SCF E_T of 6a (constrained, option A) = E(T1@cgT1) - E(S0@cgS0) = 0.08648028 Ha = 2.3532 eV = 227.05 kJ/mol, 0.437 eV (41.9 kJ/mol) below 2.79 eV. PBE fails the endorsed window, as it failed the thioxanthone calibration (-0.39 eV); the PBE deficit for 6a (-0.44 eV) is similar.

Evidence: ev-p2-energies
Provenance: session-phase2
Supersedes: none

### res-p2-pbe-vertical (result, verified)

[TOOL] Other PBE levels (h0.35, r(6,9)): vertical gap at S1 2.5120 eV; vertical emission at cgT1 E(T1@cgT1) - E(S0@cgT1) = 2.2328 eV = 215.44 kJ/mol. S0 at cgS0 recomputed with an input guess reproduces the geopt energy to 8e-9 Ha.

Evidence: ev-p2-energies
Provenance: session-phase2
Supersedes: none

### res-pbe0-memory (result, verified)

[TOOL] Measured PBE0 memory (BigDFT 1.9.5, thioxanthone, hgrid 0.35, rmult (6, 9), 8 MPI x 8 OMP, OP2P): peak RSS 30.1 GB for S0 and 48.6-52.6 GB for T1, reached during the input guess; wall time about 8.6 min (S0, 46 SCF iterations) and 37-38 min (T1, 68-72 iterations). BigDFT's own estimate (501 MB per process) is far too low for hybrids. Use these measurements to size PBE0 jobs for 6a, which has 3x the electrons and a larger grid.

Evidence: ev-runlog
Provenance: session-curation
Supersedes: none

### res-plain-xyz (result, verified)

[TOOL] BigDFT-ready plain 4-column XYZ (Angstrom) of S1 and S3: bigdft/6a_S1.xyz and bigdft/6a_S3.xyz, made by procedures/to_plain_xyz.py (stdlib), which copies the coordinate tokens verbatim (identity checked by test). Same atom order as structures/, so the thioxanthone is atoms 28-42.

Evidence: ev-structures
Provenance: session-curation
Supersedes: none

### res-s1 (result, verified)

[TOOL] S1 (6a_nmr_gfn2_ch2cl2_restrained): GFN2-xTB/ALPB(CH2Cl2) with two-sided flat-bottom Table S1 restraints (k 2.5 eV/A^2), 176 BFGS steps. Max violation 0.07 A, none > 0.3 A; type II' turn Pro 56/-126, Aib -81/1; NH...O 2.02 A; thioxanthone plane r.m.s. 0.155 A, C9=O 1.230 A. Electronic energy -3464.6577 eV (sum of the per-atom column); the BFGS log value -3464.6176 eV includes +0.040 eV restraint penalty.

Evidence: ev-runlog, ev-structures
Provenance: session-structures
Supersedes: none

### res-s2 (result, verified)

[TOOL] S2 (6a_nmr_restrained_mmff): MMFF94 with NOE and II' torsion restraints; max violation 0.24 A, none > 0.3 A; Pro 71/-126, Aib -89/15; H...O 2.41 A; E_MMFF 122.09 kcal/mol (+1.57 vs v1). Start for xTB runs. Plain 4-column XYZ.

Evidence: ev-runlog, ev-structures
Provenance: session-structures
Supersedes: none

### res-s3 (result, verified)

[TOOL] S3 (6a_nmr_gfn2_ch2cl2): unrestrained GFN2-xTB/ALPB(CH2Cl2) from S2, 237 BFGS steps, E = -3465.1108 eV. Turn kept (53/-141, -84/21) but the pTxa side chain rotates (chi1 -41 -> -61 deg); 8 restraints violated by > 0.3 A (max 1.40 A; ids 5, 6, 10, 13, 16, 19, 22, 27). Nearest local minimum; reference only, not an NMR model.

Evidence: ev-runlog, ev-structures
Provenance: session-structures
Supersedes: none

### res-strain-old (result, superseded)

[TOOL] S1 lies 0.49 eV (11.4 kcal/mol) above S3 (session value, also stated in structures/README.md).

Evidence: ev-runlog
Provenance: session-structures
Supersedes: none

### res-thioxanthone (result, verified)

[TOOL] Thioxanthone C13H8OS (23 atoms) built from SMILES O=C1c2ccccc2Sc2ccccc21 by procedures/build_thioxanthone.py: RDKit ETKDGv3 (seed 20261020) -> MMFF94 -> gas-phase GFN2-xTB BFGS (fmax 0.01 eV/A, 23 steps), E = -1067.0693 eV; planar (heavy-atom plane r.m.s. 0.0000 A), C9=O 1.222 A. Pre-optimisation only. Environment: Python 3.12.9, numpy 2.5.0, rdkit 2026.09.1, ase 3.29.0, tblite 0.7.0.

Evidence: ev-structures, ev-runlog
Provenance: session-curation
Supersedes: none

### res-tx-calib-pbe (result, verified)

[TOOL] Calibration check, PBE: 236.70 kJ/mol (2.453 eV) vs literature 274.1 kJ/mol (2.840 eV) for thioxanthone: -37.4 kJ/mol (-0.39 eV), outside the 0.2 eV calibration window. PBE alone does not pass the calibration.

Evidence: ev-phase1, ev-lit-tx
Provenance: session-curation
Supersedes: none

### res-tx-calib-pbe0 (result, verified)

[TOOL] Calibration check, PBE0: adiabatic 260.75 kJ/mol (2.702 eV) vs literature 274.1 kJ/mol (2.840 eV): -13.35 kJ/mol (-0.138 eV), inside the endorsed 0.2 eV window. The PBE0 Delta-SCF protocol passes the calibration; PBE (-0.388 eV) does not. Caveat: the literature value is from a secondary source of uncertain kind (0-0 vs onset).

Evidence: ev-phase1, ev-lit-tx
Provenance: session-curation
Supersedes: none

### res-tx-lit (result, verified)

[LITERATURE, secondary] E_T(thioxanthone) = 65.5 kcal/mol (274.1 kJ/mol, 2.840 eV) in hydroxylic solvents, as stated by Rodrigues et al., J. Braz. Chem. Soc. 2010, citing Dalton & Turro 1971 and Dalton & Montgomery 1974. That is 5 kJ/mol (0.05 eV) above E_T(6a) = 269 kJ/mol, consistent with the paper's 'comparable'.

Evidence: ev-lit-tx
Provenance: jbcs2010, session-curation
Supersedes: none

### res-tx-pbe (result, verified)

[TOOL] Thioxanthone, BigDFT 1.9.5 PBE, Krack PBE pseudopotentials, free BC, hgrid 0.35 bohr, rmult (6, 9), gnrm 1e-5, SQNM geopt from the GFN2 geometry: S0 E = -104.958932176445 Ha (converged at iteration 25, Fmax 1.21e-4 Ha/bohr); T1 (nspin 2, mpol 2, magnetization 2.000) E = -104.868778644431 Ha (iteration 30, Fmax 6.63e-5). Adiabatic Delta-SCF E_T = 0.09015353 Ha = 2.4532 eV = 236.70 kJ/mol. T1 vs S0: C9=O 1.2355 -> 1.2867 A, C9-C(ring) 1.483 -> 1.453 A, C-S 1.742 -> 1.731 A; both planar. No zero-point correction. Jobs 211185/211186, 12 MPI x 4 OMP; inputs byte-identical to the dry-run-validated files.

Evidence: ev-runlog, ev-phase1
Provenance: session-curation
Supersedes: none

### res-tx-pbe0 (result, verified)

[TOOL] Thioxanthone PBE0 single points (ixc -406, Krack PBE pseudopotentials, hgrid 0.35, rmult (6, 9), gnrm < 1e-5) at the converged PBE S0 and T1 geometries: E(S0@S0) = -104.920157843791, E(S0@T1) = -104.911685404613, E(T1@S0) = -104.815933904345, E(T1@T1) = -104.820844775510 Ha (T1 magnetization 2.000). PBE0 adiabatic E_T = 0.09931307 Ha = 2.7024 eV = 260.75 kJ/mol. Vertical absorption to T1 (at S0) 2.836 eV = 273.64 kJ/mol; vertical emission (at T1) 2.472 eV = 238.50 kJ/mol; relaxation energies T1 0.134 eV, S0 0.231 eV. No zero-point correction.

Evidence: ev-runlog, ev-phase1
Provenance: session-curation
Supersedes: none

## Source references

- chemotion-6a: https://doi.org/10.14272/WQGGCBKETYIIRM-BHIFYINESA-N.2 — Chemotion Repository molecule record of 6a (SMILES/InChI), collection 10.14272/collection/RMI_2026-01-30
- jbcs2010: https://doi.org/10.1590/S0103-50532010000600003 — Rodrigues, Silva & Netto-Ferreira, Laser flash photolysis study of the photochemistry of thioxanthone in organic solvents, J. Braz. Chem. Soc. 21 (2010); open access; secondary source for E_T(TX)
- paper: https://doi.org/10.1038/s44160-026-01173-7 — Irle, Lazzarini, Hagn, Zacharias & Bach, Photocatalytic tetrapeptides for enantioselective visible light-induced transformations, Nature Synthesis (2026); CC BY 4.0
- paper-skill: https://github.com/TengxiangLii/P2A-Robert-2026/tree/bc704b2 — Paper2Agent paper skill irle2026-tetrapeptide-photocatalysis-paper, commit bc704b2 (strict verify: reviewed_with_limitations); paper-only, no MCP server
- researcher-phase2: claude-code-session:e8098ac3-042d-4e3e-b262-6c20e3007ac3#researcher — Researcher's instructions and decisions in the same session (Phase 2 scope, geometry strategy, job cancellations, capsulization)
- researcher-request: claude-code-session:e3e745d8-25c4-4f71-9ca9-1ce91da60329#request — Researcher's objective: build a capsule from the agentified paper, BigDFT skills and Capsule-Maker, and reproduce the experimental E_T = 269 kJ/mol of 6a with BigDFT; endorsements and the dry-run requirement given in the same session on 2026-10-20
- session-curation: claude-code-session:e3e745d8-25c4-4f71-9ca9-1ce91da60329 — Claude Code session (Claude Opus 5.5), 2026-10-20, that curated this capsule from the primary sources and re-derived energies, indices and hashes from the packaged files
- session-phase2: claude-code-session:e8098ac3-042d-4e3e-b262-6c20e3007ac3 — Claude Code session (Claude Opus 5.5), 2026-10-22, that resumed C1, ran Phase 2 on TSUBAME4.0 and curated these records
- session-structures: claude-code-session:b8d95464-d0d1-43eb-b855-93baccca4203 — Claude Code session (Claude Opus 5.5), 2026-10-15 08:46-09:00 UTC, in which the 6a structures were built; tool-call IDs in evidence/run_log.md; transcript retained by the researcher, not packaged
- si: https://doi.org/10.1038/s44160-026-01173-7 — Supplementary Information of the paper (general methods, S4 NMR, Table S1 restraints)
- tsubame4-runs: urn:capsule-6a:tsubame4:phase2-2026-10-22 — BigDFT runs on TSUBAME4.0, jobs 9098971-9102503; full logs in external artifact phase2-results-logs-20261022

## Conflicts

None declared or detected.

## Evolution

Parent: sha256:e7fb9b94c73e78b8b9dae05a35a34721d4c4bf8755ff23c908e6a3767b951661
New records: cor-p2-t1-scf, ctx-p2-disk, ctx-p2-request, ctx-p2-tsubame, dec-p2-geopt-constrained, dec-p2-geopt-free, dec-p2-grid, ev-p2-dryruns, ev-p2-energies, ev-p2-geometries, ev-p2-runs, fail-p2-restart-displaced, fail-p2-t1-itermax, hyp-p2-t1-frontier, proc-p2-restart, proc-p2-workflow, q-p2-absorption, q-p2-pbe0, res-p2-cgeopt, res-p2-dryrun, res-p2-free-s0, res-p2-free-t1-partial, res-p2-grid, res-p2-pbe-adiabatic, res-p2-pbe-vertical
Revised statuses: dec-tx-grid

## External artifacts (not automatically fetched)

- phase2-results-logs-20261022: file:phase2-results-logs-20261022.tar.gz (SHA-256 bdfa980c45a3aee53d5bb33e620f48671b2020b5c0fef1dc2044eb22e36f1d85, 7602737 bytes)

## Environment

Python >=3.10
- ase>=3.29,<3.30
- numpy>=2,<3
- pybigdft>=1.9.6,<1.10
- pyyaml>=6
- rdkit>=2026.9.1,<2027
- tblite>=0.7,<0.8

## Receiving instructions

Inspect the manifest, knowledge, evidence, procedures, and tests before approval.
Verify integrity and environment requirements. Import/inspection never run code.
Run tests only after explicit trust using `capsule-maker verify PATH --trust-code`.
Checksums establish integrity, not authorship or scientific validity.
