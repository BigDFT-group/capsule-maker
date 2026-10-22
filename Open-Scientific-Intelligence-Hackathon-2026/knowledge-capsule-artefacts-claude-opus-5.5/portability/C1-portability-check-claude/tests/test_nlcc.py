"""Stdlib checks of the NLCC thioxanthone portability results against their logs, inputs and the inherited C1 data."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
N = ROOT / "nlcc"
HA_EV, HA_KJ = 27.211386245988, 2625.4996394799
SUMMARY = json.loads((N / "nlcc_summary.json").read_text())
C1 = json.loads((ROOT / "bigdft" / "runs" / "phase1_summary.json").read_text())


def energy(name):
    t = (N / "runs" / name / f"log-{name}.yaml").read_text()
    return float(re.findall(r"Energy \(Hartree\)\s*:\s*(\S+)", t)[-1])


class NLCC(unittest.TestCase):
    def test_all_runs_converged(self):
        self.assertEqual(len(SUMMARY["runs"]), 10)
        for name, r in SUMMARY["runs"].items():
            self.assertTrue(r["converged"], name)
            if "_T1_" in name:
                self.assertAlmostEqual(r["magnetization"], 2.0, places=6, msg=name)

    def test_summary_matches_logs(self):
        for name, r in SUMMARY["runs"].items():
            self.assertAlmostEqual(energy(name), r["energy_Ha"], places=9, msg=name)

    def test_control_reproduces_c1(self):
        for st in ("S0", "T1"):
            e = energy(f"tx_{st}_pbe_krack_at_{st}pbe")
            self.assertLess(abs(e - C1[st]["energy_Ha"]), 1e-7, st)

    def test_adiabatic_triplet_energies(self):
        for xc, kj in (("pbe", 241.21), ("pbe0", 264.17)):
            d = energy(f"tx_T1_{xc}_nlcc_at_T1pbe") - energy(f"tx_S0_{xc}_nlcc_at_S0pbe")
            self.assertAlmostEqual(d * HA_KJ, kj, places=1, msg=xc)
            self.assertAlmostEqual(SUMMARY[xc.upper() + "_NLCC"]["adiabatic"]["kJ_mol"], kj, places=2)

    def test_calibration_verdicts(self):
        lit_ev = 274.1 / HA_KJ * HA_EV
        self.assertGreater(abs(SUMMARY["PBE_NLCC"]["adiabatic"]["eV"] - lit_ev), 0.2)
        self.assertLessEqual(abs(SUMMARY["PBE0_NLCC"]["adiabatic"]["eV"] - lit_ev), 0.2)

    def test_pseudopotential_assignment(self):
        for f in sorted((N / "inputs").glob("*.yaml")):
            blocks = dict(re.findall(r"^psppar\.(\w+):\n((?:  .*\n)+)", f.read_text(), flags=re.M))
            self.assertEqual(set(blocks), {"C", "H", "O", "S"}, f.name)
            nval = {e: int(re.search(r"No\. of Electrons: (\d+)", b).group(1)) for e, b in blocks.items()}
            self.assertEqual(sum(nval[e] * n for e, n in {"C": 13, "H": 8, "O": 1, "S": 1}.items()), 72, f.name)
            self.assertIn("Goedecker pseudopotential", blocks["S"], f.name)  # no NLCC file for S
            if "_nlcc_" in f.name:
                for e in ("C", "O"):
                    self.assertIn("HGH-K + NLCC", blocks[e], f"{f.name} {e}")
                self.assertIn("Saha", blocks["H"], f.name)
            else:
                for e in "CHO":
                    self.assertIn("Goedecker pseudopotential", blocks[e], f"{f.name} {e}")

    def test_geometries_are_c1_pbe_minima(self):
        for geo in ("S0", "T1"):
            ref = (ROOT / "bigdft" / "runs" / f"tx_{geo}_pbe_geopt" / f"final_tx_{geo}_pbe_geopt.yaml").read_text()
            ref_pos = re.findall(r"- (\w+): \[([^\]]+)\]", ref)
            for f in (N / "inputs").glob(f"*_at_{geo}pbe.yaml"):
                pos = re.findall(r"- (\w+): \[([^\]]+)\]", f.read_text().split("posinp:")[1])
                self.assertEqual(len(pos), 23, f.name)
                for (e1, c1), (e2, c2) in zip(ref_pos, pos):
                    self.assertEqual(e1, e2)
                    for a, b in zip(c1.split(","), c2.split(",")):
                        self.assertAlmostEqual(float(a), float(b), places=12, msg=f.name)


if __name__ == "__main__":
    unittest.main()
