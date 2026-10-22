#!/usr/bin/env python3
"""Write session-phase2/memory.json (Capsule-Maker local-JSON memory, format 1.1) for the C1 -> C2 extension.

Records are curated from this session's TSUBAME runs; numbers come from the packaged evidence
(phase2/evidence/*.json), which is regenerated from the logs by phase2/analysis/collect_evidence.py.
Usage: python3 capsule-C2/build_memory.py   (from the knowledge-growth-remote directory)
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SESSION = HERE / "session-phase2"
ARCHIVE = HERE / "phase2-results-logs-20261022.tar.gz"
TAG = "6a-phase2"
EXT_ID = "phase2-results-logs-20261022"

records = []


def rec(id, kind, status, content, *, evidence=(), artifacts=(), references=(), supersedes=(),
        provenance=("session-phase2",), external=()):
    item = {"id": id, "kind": kind, "status": status, "content": content, "tags": [TAG],
            "references": list(references), "evidence": list(evidence), "artifacts": list(artifacts),
            "provenance": list(provenance), "supersedes": list(supersedes), "contradicts": [],
            "sensitive": False}
    if external:
        item["external_artifacts"] = list(external)
    records.append(item)


INPUTS = [f"phase2/inputs/{s}.yaml" for s in (
    "01_t1_scf_rerun", "02_pbe_s1_wavefunctions", "03_pbe0_s1_vertical", "04_geopt_free",
    "05_geopt_constrained", "06_pbe_cg_wavefunctions", "07_pbe0_cg")]
SCRIPTS = sorted(f"phase2/scripts/{p.name}" for p in (SESSION / "phase2/scripts").glob("*.sh"))
LISTS = sorted(f"phase2/scripts/lists/{p.name}" for p in (SESSION / "phase2/scripts/lists").glob("*.list"))
ANALYSIS = ["phase2/analysis/analyze_6a.py", "phase2/analysis/summarize.py", "phase2/analysis/collect_evidence.py"]
GEOMS = ["phase2/geometries/6a_cgS0_pbe.xyz", "phase2/geometries/6a_cgT1_pbe.xyz", "phase2/geometries/6a_freeS0_pbe.xyz"]
EVID = ["phase2/evidence/energies.json", "phase2/evidence/summary.json",
        "phase2/evidence/phase2_grid_pbe_50iter.json", "phase2/evidence/phase2_grid_pbe_converged.json"]

rec("ctx-p2-request", "context", "verified",
    "[RESEARCHER, 2026-10-22] Phase 2 request: run the 24 dry-run-validated PBE grid-convergence inputs on 6a S1 "
    "(S0 and T1), then PBE0 single points on 6a, and compare with the endorsed 2.79 +/- 0.15 eV; run the "
    "calculations on TSUBAME4.0. Later: keep the jobs running as they are and capsulize the Phase 2 state.",
    evidence=["ev-p2-runs"], references=["dec-criteria-ok", "res-dryrun"], provenance=("researcher-phase2",))
rec("ctx-p2-tsubame", "context", "verified",
    "[TOOL] Phase 2 ran on TSUBAME4.0 (AMD EPYC 9654 nodes, Altair Grid Engine, 24 h job limit) with a user-built "
    "BigDFT (libbigdft 1.9.5, PSolver 1.10, futile 1.9, CHESS 0.2.4, libxc 4.3.4; GCC + OpenMPI 5.0.7), identical "
    "library versions to ctx-env; PyBigDFT 1.9.6 in conda. Modules cuda/12.8.0, openmpi/5.0.7-gcc, intel/2025.0.0, "
    "UCX LD_PRELOAD, OMPI_MCA_coll=^hcoll (scripts/bigdft_env.sh). Launch: mpirun -np N --map-by slot:PE=OMP "
    "(fail-srun lesson). PBE runs: cpu_80 (80 cores, 184 GB) as 20 MPI x 4 OMP; PBE0: node_f (192 cores, "
    "768 GB) as 24 MPI x 8 OMP. GPUs unused.",
    evidence=["ev-p2-runs"], artifacts=["phase2/scripts/bigdft_env.sh", "phase2/evidence/run_record.md"],
    references=["ctx-env", "fail-srun"], provenance=("session-phase2", "tsubame4-runs"))
rec("res-p2-dryrun", "result", "verified",
    "[TOOL] dec-dryrun-first honoured on TSUBAME: bigdft-tool memory estimation passed for the 24 C1 Phase 2 inputs "
    "and for all 30 new inputs (stages 01-07, incl. the superseded cold-start PBE0 pair); 226 electrons each, no "
    "BigDFT error block. PBE0 inputs read as ixc -406 with only the expected 'PSP generated with a different XC' "
    "warning. Estimated peaks (16 processes) 0.85-4.4 GB per process; not valid for exact-exchange memory.",
    evidence=["ev-p2-dryruns"], references=["dec-dryrun-first", "res-dryrun", "fail-pbe0-oom"])
rec("fail-p2-t1-itermax", "failed_attempt", "superseded",
    "[TOOL] With BigDFT defaults (itermax 50, nrepmax 1) all 12 T1 single points at S1 stopped unconverged "
    "(gnrm 6.6e-5 to 1.5e-4 > gnrm_cv 1e-5) while S0 converged in 23-25 iterations. The resulting vertical gap "
    "2.547 eV was 35 meV too high; T1 energies were still falling by up to 37 meV.",
    evidence=["ev-p2-energies"])
rec("cor-p2-t1-scf", "correction", "verified",
    "[TOOL] 6a T1 needs dft itermax 200 and nrepmax 5: all 12 T1 reruns converged below 1e-5 after 490-560 SCF "
    "iterations (15 min to 1 h 37 min on 20 MPI x 4 OMP), magnetisation 2.000. All later T1 inputs carry these settings.",
    evidence=["ev-p2-energies"], artifacts=["phase2/inputs/01_t1_scf_rerun.yaml"], supersedes=["fail-p2-t1-itermax"])
rec("hyp-p2-t1-frontier", "hypothesis", "hypothesis",
    "[AI interpretation] Slow T1 convergence: the highest occupied spin-down levels are closely spaced (-0.192, "
    "-0.201, -0.202, -0.209 Ha in the first T1 run), probably peptide amide/carbonyl lone pairs that PBE places near "
    "the thioxanthone levels, so the triplet hole can move between them. Not yet tested by spin-density or orbital analysis.",
    evidence=["ev-p2-energies"], references=["q-t1-character"])
rec("res-p2-grid", "result", "verified",
    "[TOOL] PBE vertical Delta-SCF gap of 6a at S1 (converged T1): 2.5114-2.5126 eV over hgrid 0.45/0.40/0.35/0.30 x "
    "rmult (5,8)/(6,9)/(7,10), a 1.2 meV spread; 2.5120 eV = 242.37 kJ/mol at hgrid 0.35, rmult (6,9), 0.4 meV from "
    "the finest grid. Absolute S0 energies change by 0.1 Ha over the same range; the gap does not.",
    evidence=["ev-p2-energies"])
rec("dec-p2-grid", "decision", "verified",
    "[AI decision, evidence-backed] Use hgrid 0.35 bohr, rmult (6,9) for all 6a production runs. res-p2-grid shows "
    "the triplet gap converged to < 1 meV there, which also verifies the provisional thioxanthone grid of dec-tx-grid "
    "(same settings), so the calibration and 6a share one converged grid.",
    evidence=["ev-p2-energies"], references=["res-p2-grid"], supersedes=["dec-tx-grid"])
rec("dec-p2-geopt-free", "decision", "superseded",
    "[RESEARCHER, 2026-10-22] For the adiabatic E_T, optimise 6a S0 and T1 with fully free PBE geometry "
    "optimisations from S1 (chosen over a backbone-constrained or vertical-only approach).",
    evidence=["ev-p2-runs"], provenance=("researcher-phase2",))
rec("dec-p2-geopt-constrained", "decision", "verified",
    "[RESEARCHER, 2026-10-22] Switch the main path to option A: relax only the thioxanthone (0-based atoms 28-42 "
    "plus its 7 H, 70-76; C2 ring position bonded to pTxa C-beta 27) with the other 55 atoms frozen at S1, in both "
    "S0 and T1; keep the free runs as a sensitivity check. Reasons discussed: dec-select warns that free DFT "
    "relaxation leaves the NMR conformation, and E_T is measured in a 77 K glass. The free T1 run was later "
    "cancelled at the researcher's request.",
    evidence=["ev-p2-runs"], references=["dec-select", "res-s3", "cor-index"], supersedes=["dec-p2-geopt-free"],
    provenance=("researcher-phase2",))
rec("proc-p2-workflow", "procedure", "verified",
    "[TOOL] Stage pipeline (phase2/inputs): 01 T1 reruns; 02 PBE at S1 writing wavefunctions; 03 PBE0 at S1 "
    "(restart from 02); 04 free SQNM geopt; 05 constrained SQNM geopt (Frozen: fxyz on 55 atoms, restart from 02); "
    "06 PBE at the constrained minima writing wavefunctions; 07 PBE0 at the constrained minima (restart from 06). "
    "Geopt settings as the thioxanthone protocol (SQNM, 300 steps, betax 1.0, forcemax 2e-4, frac_fluct 1.0). "
    "Grid Engine array jobs via scripts/run_array*.sh; every input passes scripts/dryrun_dir.sh first; "
    "analysis/collect_evidence.py condenses logs into the evidence files; tests/test_phase2_evidence.py checks them.",
    evidence=["ev-p2-runs", "ev-p2-energies"],
    artifacts=INPUTS + SCRIPTS + LISTS + ANALYSIS + ["phase2/RECEIVING-PHASE2.md", "tests/test_phase2_evidence.py"],
    references=["proc-inputs", "dec-dryrun-first"])
rec("proc-p2-restart", "procedure", "verified",
    "[TOOL] Wavefunction restart: write with output: {orbitals: binary}, then copy the whole data-<src> directory "
    "(glr.dat, wavefunction.yaml, wavefunction-*.bin) to data-<name> and set dft inputpsiid: 2. At an unchanged "
    "geometry the restart converges in 2 iterations to the same energy (2e-9 Ha). Copying only the wavefunction "
    "files fails (glr.dat missing). Atomic-orbital files are not needed.",
    evidence=["ev-p2-runs"], artifacts=["phase2/scripts/restart_test.sh", "phase2/scripts/restart_test2.sh",
                                        "phase2/scripts/run_array_rst.sh", "phase2/scripts/run_array_rst2.sh",
                                        "phase2/scripts/run_array_rst3.sh"])
rec("fail-p2-restart-displaced", "failed_attempt", "verified",
    "[TOOL] Restarting from S1 wavefunctions at the constrained T1 minimum (max displacement 0.56 A) gives a poor "
    "guess (iteration 1: -337.7 Ha, gnrm 0.78), no better than an input guess. Hence stage 06 recomputes PBE "
    "wavefunctions at the exact target geometries before the PBE0 restart.",
    evidence=["ev-p2-runs"], artifacts=["phase2/scripts/restart_test3.sh"])
rec("res-p2-cgeopt", "result", "verified",
    "[TOOL] Constrained PBE minima (option A): S0 converged in 68 SQNM steps, T1 in 94 (Fmax 3.4e-4 and 3.8e-4 "
    "Ha/bohr, below the force noise 5.0e-4 and 8.9e-4; stop by frac_fluct, as in Phase 1). Only atoms 28-42 and "
    "70-76 moved (max 0.29 A in S0, 0.56 A in T1). C34=O35 1.240 A (S0) and 1.288 A (T1), cf. thioxanthone "
    "1.236 -> 1.287 A. Relaxation energies from S1: S0 -0.159 eV, T1 -0.318 eV (part of each is the GFN2 -> PBE "
    "geometry change).",
    evidence=["ev-p2-energies", "ev-p2-geometries"],
    artifacts=["phase2/inputs/05_geopt_constrained.yaml", "phase2/geometries/6a_cgS0_pbe.xyz",
               "phase2/geometries/6a_cgT1_pbe.xyz"], references=["res-tx-pbe"])
rec("res-p2-pbe-adiabatic", "result", "verified",
    "[TOOL] PBE adiabatic Delta-SCF E_T of 6a (constrained, option A) = E(T1@cgT1) - E(S0@cgS0) = 0.08648028 Ha = "
    "2.3532 eV = 227.05 kJ/mol, 0.437 eV (41.9 kJ/mol) below 2.79 eV. PBE fails the endorsed window, as it failed "
    "the thioxanthone calibration (-0.39 eV); the PBE deficit for 6a (-0.44 eV) is similar.",
    evidence=["ev-p2-energies"], references=["res-tx-calib-pbe", "dec-criteria-ok", "res-p2-cgeopt"])
rec("res-p2-pbe-vertical", "result", "verified",
    "[TOOL] Other PBE levels (h0.35, r(6,9)): vertical gap at S1 2.5120 eV; vertical emission at cgT1 "
    "E(T1@cgT1) - E(S0@cgT1) = 2.2328 eV = 215.44 kJ/mol. S0 at cgS0 recomputed with an input guess reproduces "
    "the geopt energy to 8e-9 Ha.",
    evidence=["ev-p2-energies"], artifacts=["phase2/inputs/06_pbe_cg_wavefunctions.yaml"])
rec("res-p2-free-s0", "result", "verified",
    "[TOOL] Free PBE S0 geopt from S1 converged in 86 steps (Fmax 3.3e-4) at -358.886769 Ha, 0.42 eV below the "
    "constrained S0 minimum: the unconstrained peptide relaxes away from the NMR-fitted conformation, as S3 did "
    "with GFN2-xTB.",
    evidence=["ev-p2-energies", "ev-p2-geometries"],
    artifacts=["phase2/inputs/04_geopt_free.yaml", "phase2/geometries/6a_freeS0_pbe.xyz"], references=["res-s3"])
rec("res-p2-free-t1-partial", "result", "unverified",
    "[TOOL] Free PBE T1 geopt was cancelled after ~108 steps (Fmax ~2e-3, not converged) at -358.800552 Ha; with "
    "the free S0 minimum this gives a provisional 2.346 eV, close to the constrained 2.353 eV, suggesting the "
    "peptide conformation affects E_T little. Not a converged result.",
    evidence=["ev-p2-energies"])
rec("ctx-p2-disk", "context", "verified",
    "[TOOL] TSUBAME storage: /work counts against the 125 GB home quota; output: {orbitals: binary} writes 6-12 GB "
    "per 6a state, about two thirds of it atomic-orbital files not needed for restarts. Superfluous files were "
    "moved to a group disk; plan disk before chaining wavefunction restarts.",
    evidence=["ev-p2-runs"])
rec("q-p2-pbe0", "question", "unresolved",
    "Next action and open criterion: PBE0 single points at the constrained minima (stage 07: S0@cgS0, T1@cgT1, "
    "T1@cgS0, S0@cgT1; job 9102503) and at S1 (stage 03; job 9100870) were queued, not finished, when C2 was "
    "made. The endorsed test is PBE0 adiabatic E(T1@cgT1) - E(S0@cgS0) within 2.79 +/- 0.15 eV. If PBE0 shifts "
    "6a as it shifted thioxanthone (+0.25 eV), E_T would be near 2.6 eV, at the lower edge; this is an "
    "extrapolation, not a result.",
    evidence=["ev-p2-runs"], references=["dec-criteria-ok", "res-functional-effect", "res-p2-pbe-adiabatic"])
rec("q-p2-absorption", "question", "unresolved",
    "PBE T1@cgS0 (vertical absorption partner, stage 06) and T1@cgT1 single point with wavefunctions were still "
    "running when C2 was made.",
    evidence=["ev-p2-runs"])
rec("ev-p2-energies", "evidence", "verified",
    "[TOOL] Condensed numbers from every Phase 2 BigDFT log (final energies, SCF iterations, gnrm, magnetisation, "
    "MPI/OMP, geopt forces) with each full log's SHA-256, plus the E_T summary and both grid-study tables; full "
    "logs in the external archive.",
    artifacts=EVID, external=[EXT_ID])
rec("ev-p2-dryruns", "evidence", "verified",
    "[TOOL] bigdft-tool memory-estimation results of all Phase 2 dry runs (54 entries).",
    artifacts=["phase2/evidence/dryruns.json"])
rec("ev-p2-geometries", "evidence", "verified",
    "[TOOL] Plain XYZ (A) of the PBE constrained S0/T1 minima and the free S0 minimum, extracted from the BigDFT "
    "final_*.yaml files by analysis/collect_evidence.py; same atom order as C1 bigdft/6a_S1.xyz.",
    artifacts=GEOMS)
rec("ev-p2-runs", "evidence", "verified",
    "[TOOL] TSUBAME job record of Phase 2 (job IDs, resources, outcomes, cancellations) and the exact inputs of every stage.",
    artifacts=["phase2/evidence/run_record.md"] + INPUTS)

roles = {p: "procedure" for p in SCRIPTS + ANALYSIS}
roles.update({p: "data" for p in INPUTS + LISTS + GEOMS})
roles.update({p: "evidence" for p in EVID + ["phase2/evidence/dryruns.json", "phase2/evidence/run_record.md"]})
roles["phase2/RECEIVING-PHASE2.md"] = "instructions"
roles["tests/test_phase2_evidence.py"] = "test"
missing = [p for p in roles if not (SESSION / p).is_file()]
assert not missing, missing

memory = {
    "format_version": "1.1",
    "origin": {"backend": "local-json",
               "description": "Curated by the agent from this session's TSUBAME4.0 Phase 2 runs (logs, dry runs, job "
                              "record) and the researcher's decisions of 2026-10-22; provenance classes [TOOL]/[RESEARCHER]/[AI]"},
    "records": records,
    "sources": [
        {"id": "session-phase2", "uri": "claude-code-session:e8098ac3-042d-4e3e-b262-6c20e3007ac3",
         "description": "Claude Code session (Claude Opus 5.5), 2026-10-22, that resumed C1, ran Phase 2 on TSUBAME4.0 and curated these records"},
        {"id": "researcher-phase2", "uri": "claude-code-session:e8098ac3-042d-4e3e-b262-6c20e3007ac3#researcher",
         "description": "Researcher's instructions and decisions in the same session (Phase 2 scope, geometry strategy, job cancellations, capsulization)"},
        {"id": "tsubame4-runs", "uri": "urn:capsule-6a:tsubame4:phase2-2026-10-22",
         "description": "BigDFT runs on TSUBAME4.0, jobs 9098971-9102503; full logs in external artifact " + EXT_ID},
    ],
    "python": ">=3.10",
    "artifacts": [{"path": p, "role": r, "packages": []} for p, r in sorted(roles.items())],
    "external_artifacts": [{
        "id": EXT_ID,
        "uri": "file:phase2-results-logs-20261022.tar.gz",
        "sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        "size": ARCHIVE.stat().st_size,
        "description": "Full Phase 2 BigDFT logs, dry-run outputs and job logs as of 2026-10-22 ~21:00 JST "
                       "(wavefunction data directories excluded); snapshot taken while stages 03, 06 (T1) and 07 were unfinished",
        "dependencies": [],
        "required_for_reproduction": False,
    }],
}
(SESSION / "memory.json").write_text(json.dumps(memory, indent=2) + "\n")
print(f"{len(records)} records, {len(roles)} artifacts -> {SESSION / 'memory.json'}")
