"""Stdlib checks of the packaged Phase 2 evidence: energies, convergence, constraints, geometries."""
import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P2 = ROOT / "phase2"
HA_EV = 27.211386245988
HA_KJ = 2625.4996394799
MOBILE = list(range(28, 43)) + list(range(70, 77))  # thioxanthone heavy atoms + its 7 H (0-based)
GRIDS = [f"h{h}_r{r}" for h in ("0.45", "0.40", "0.35", "0.30") for r in ("5-8", "6-9", "7-10")]


def energies():
    return json.loads((P2 / "evidence" / "energies.json").read_text())


def E(key):
    run = energies()[key]
    assert run["finished"], key
    return run["energy_Ha"]


def xyz(path):
    lines = Path(path).read_text().splitlines()
    n = int(lines[0])
    return [(t[0], tuple(float(c) for c in t[1:4])) for t in (l.split() for l in lines[2:2 + n])]


def docs(stage):
    text = (P2 / "inputs" / f"{stage}.yaml").read_text()
    parts = re.split(r"^--- # (\S+)\n", text, flags=re.M)[1:]
    return dict(zip(parts[0::2], parts[1::2]))


class Convergence(unittest.TestCase):
    def test_final_runs_converged(self):
        final = [k for k in energies() if k.startswith(("00_phase2_grid_pbe/6a_S1_S0", "01_", "02_", "05_"))]
        self.assertEqual(len(final), 12 + 12 + 2 + 2)
        for k in final:
            run = energies()[k]
            self.assertTrue(run["finished"], k)
            self.assertLess(run["last_gnrm"], 1e-5, k)
            self.assertEqual(run["electrons"], 226, k)

    def test_first_pass_t1_was_unconverged(self):
        # fail-p2-t1-itermax: the default itermax 50 left every T1 above gnrm_cv
        t1 = [v for k, v in energies().items() if k.startswith("00_phase2_grid_pbe/6a_S1_T1")]
        self.assertEqual(len(t1), 12)
        self.assertTrue(all(v["last_gnrm"] > 1e-5 for v in t1))

    def test_t1_is_triplet(self):
        for k, v in energies().items():
            if "_T1_" in k and v["finished"]:
                self.assertAlmostEqual(v["magnetization"], 2.0, places=3, msg=k)

    def test_constrained_geopts_stopped_on_force_noise(self):
        for s in ("S0", "T1"):
            run = energies()[f"05_geopt_constrained/6a_{s}_pbe_cgeopt"]
            self.assertTrue(run["sqnm_converged"])
            self.assertLess(run["final_fmax_Ha_bohr"], run["final_force_fluct_Ha_bohr"])
            self.assertLess(run["final_fmax_Ha_bohr"], 4e-4)


class TripletEnergies(unittest.TestCase):
    def test_grid_convergence_of_vertical_gap(self):
        gaps = [(E(f"01_t1_scf_rerun/6a_S1_T1_pbe_{g}") - E(f"00_phase2_grid_pbe/6a_S1_S0_pbe_{g}")) * HA_EV
                for g in GRIDS]
        self.assertLess(max(gaps) - min(gaps), 0.002)
        self.assertAlmostEqual(gaps[GRIDS.index("h0.35_r6-9")], 2.5120, places=4)

    def test_restart_runs_reproduce_energies(self):
        self.assertAlmostEqual(E("02_pbe_s1_wavefunctions/6a_S1_S0_pbe_h0.35_r6-9"),
                               E("00_phase2_grid_pbe/6a_S1_S0_pbe_h0.35_r6-9"), delta=1e-7)
        self.assertAlmostEqual(E("02_pbe_s1_wavefunctions/6a_S1_T1_pbe_h0.35_r6-9"),
                               E("01_t1_scf_rerun/6a_S1_T1_pbe_h0.35_r6-9"), delta=1e-6)
        self.assertAlmostEqual(E("06_pbe_cg_wavefunctions/6a_cgS0_S0_pbe_h0.35_r6-9"),
                               E("05_geopt_constrained/6a_S0_pbe_cgeopt"), delta=1e-7)

    def test_pbe_adiabatic_constrained(self):
        d = E("05_geopt_constrained/6a_T1_pbe_cgeopt") - E("05_geopt_constrained/6a_S0_pbe_cgeopt")
        self.assertAlmostEqual(d * HA_EV, 2.3532, places=4)
        self.assertAlmostEqual(d * HA_KJ, 227.05, places=2)
        self.assertGreater(abs(d * HA_EV - 2.79), 0.15)  # PBE fails the endorsed window, as for thioxanthone

    def test_pbe_vertical_emission_at_cgT1(self):
        d = E("05_geopt_constrained/6a_T1_pbe_cgeopt") - E("06_pbe_cg_wavefunctions/6a_cgT1_S0_pbe_h0.35_r6-9")
        self.assertAlmostEqual(d * HA_EV, 2.2328, places=4)

    def test_free_s0_lies_below_constrained_s0(self):
        d = E("05_geopt_constrained/6a_S0_pbe_cgeopt") - E("04_geopt_free/6a_S0_pbe_geopt")
        self.assertAlmostEqual(d * HA_EV, 0.42, delta=0.01)


class Constraints(unittest.TestCase):
    def test_frozen_atoms_in_constrained_inputs(self):
        for name, body in docs("05_geopt_constrained").items():
            pos = body[body.index("posinp:"):]
            atoms = re.findall(r"^  - (\{?)[A-Z][a-z]?: \[.*$", pos, re.M)
            self.assertEqual(len(atoms), 77, name)
            lines = [l for l in pos.splitlines() if re.match(r"^  - \{?[A-Z][a-z]?: \[", l)]
            mobile = [i for i, l in enumerate(lines) if "Frozen" not in l]
            self.assertEqual(mobile, MOBILE, name)
            self.assertTrue(all("Frozen: fxyz" in lines[i] for i in range(77) if i not in MOBILE))

    def test_only_thioxanthone_moved(self):
        ref = xyz(ROOT / "bigdft" / "6a_S1.xyz")
        for g, co in (("cgS0", 1.2397), ("cgT1", 1.2884)):
            new = xyz(P2 / "geometries" / f"6a_{g}_pbe.xyz")
            self.assertEqual([e for e, _ in ref], [e for e, _ in new])
            moved = [i for i, ((_, a), (_, b)) in enumerate(zip(ref, new)) if math.dist(a, b) > 1e-6]
            self.assertTrue(set(moved) <= set(MOBILE), g)
            self.assertAlmostEqual(math.dist(new[34][1], new[35][1]), co, places=3)

    def test_pbe0_inputs_use_constrained_geometries(self):
        for name, body in docs("07_pbe0_cg").items():
            geo = re.match(r"6a_(cg[ST][01])_", name).group(1)
            coords = [tuple(float(c) for c in m.split(","))
                      for m in re.findall(r"^  - [A-Z][a-z]?: \[([^\]]+)\]", body, re.M)]
            ref = [c for _, c in xyz(P2 / "geometries" / f"6a_{geo}_pbe.xyz")]
            self.assertEqual(len(coords), 77)
            self.assertLess(max(math.dist(a, b) for a, b in zip(coords, ref)), 1e-6, name)
            self.assertIn("ixc: PBE0", body)
            self.assertIn("inputpsiid: 2", body)


class DryRuns(unittest.TestCase):
    def test_every_input_dry_run_passed(self):
        dry = json.loads((P2 / "evidence" / "dryruns.json").read_text())
        self.assertGreaterEqual(len(dry), 54)
        for k, v in dry.items():
            self.assertFalse(v["bigdft_error_block"], k)
            self.assertEqual(v["electrons"], 226, k)
            self.assertIsNotNone(v["estimated_peak_MB_per_process_16proc"], k)


if __name__ == "__main__":
    unittest.main()
