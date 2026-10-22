"""Stdlib checks of the packaged 6a structures, restraint data and experimental target."""
import csv
import json
import hashlib
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ST = ROOT / "structures"

SHA = {
    "6a_nmr_gfn2_ch2cl2_restrained.xyz": "89545776deb8d6f59a3677191be5ec6830f57d40a130fd74706a782185af27c5",
    "6a_nmr_gfn2_ch2cl2_restrained.mol": "841ae8c09502b50691b367ce04d124faa3ebc83c08a4ad32b7c61b764c537cda",
    "6a_nmr_gfn2_ch2cl2.xyz": "c4c0ab385305fee73ea5dca0e11dae5c56d61164c1b666d653fa506fbc807139",
    "6a_nmr_gfn2_ch2cl2.mol": "273693d90d7a4cf0719f740c07eb944a6bfb785e569fe6e0314081ddb8aa412f",
    "6a_nmr_restrained_mmff.xyz": "b8c984d40c0060fa84a538ac370190c93e13b88936be7d997de4226831c30b08",
    "6a_nmr_restrained_mmff.mol": "3bfebb22b4c1bad8462913ddefc1a1642b2b4677694d5942decaf302a53e735f",
}
S1, S2, S3 = "6a_nmr_gfn2_ch2cl2_restrained.xyz", "6a_nmr_restrained_mmff.xyz", "6a_nmr_gfn2_ch2cl2.xyz"


def xyz(name):
    lines = (ST / name).read_text().splitlines()
    n = int(lines[0])
    return [l.split() for l in lines[2:2 + n]]


class Structures(unittest.TestCase):
    def test_hashes(self):
        for f, h in SHA.items():
            self.assertEqual(hashlib.sha256((ST / f).read_bytes()).hexdigest(), h, f)

    def test_composition_and_explicit_h(self):
        for f in (S1, S2, S3):
            self.assertEqual(Counter(r[0] for r in xyz(f)), Counter(C=31, H=34, N=4, O=7, S=1), f)

    def test_heavy_atoms_first(self):
        el = [r[0] for r in xyz(S1)]
        self.assertNotIn("H", el[:43])
        self.assertEqual(set(el[43:]), {"H"})

    def test_thioxanthone_indices(self):
        for f in (S1, S2, S3):
            el = [r[0] for r in xyz(f)]
            self.assertEqual("".join(el[28:43]), "CCCCCCCOCCSCCCC", f)
            self.assertEqual((el[38], el[35], el[34], el[27]), ("S", "O", "C", "C"), f)

    def test_columns(self):
        self.assertEqual({len(r) for r in xyz(S1)}, {9})
        self.assertEqual({len(r) for r in xyz(S3)}, {9})
        self.assertEqual({len(r) for r in xyz(S2)}, {4})

    def test_s1_s3_electronic_gap(self):
        e1 = sum(float(r[4]) for r in xyz(S1))
        e3 = sum(float(r[4]) for r in xyz(S3))
        self.assertAlmostEqual(e1, -3464.6577, places=3)
        self.assertAlmostEqual(e3, -3465.1108, places=3)
        self.assertAlmostEqual(e1 - e3, 0.453, places=3)

    def test_s1_log_includes_restraint_penalty(self):
        last = (ST / "6a_nmr_gfn2_ch2cl2_restrained.log").read_text().split()
        e_log = float([t for t in last if re.fullmatch(r"-\d+\.\d+", t)][-1])
        self.assertAlmostEqual(e_log, -3464.6176, places=3)
        self.assertAlmostEqual(e_log - sum(float(r[4]) for r in xyz(S1)), 0.040, places=3)


class BigDFTInputs(unittest.TestCase):
    BD = ROOT / "bigdft"

    def rows(self, name):
        lines = (self.BD / name).read_text().splitlines()
        n = int(lines[0])
        return [l.split() for l in lines[2:2 + n]]

    def test_plain_xyz_is_verbatim_copy(self):
        for plain, src in (("6a_S1.xyz", S1), ("6a_S3.xyz", S3)):
            rows = self.rows(plain)
            self.assertEqual({len(r) for r in rows}, {4}, plain)
            self.assertEqual(rows, [r[:4] for r in xyz(src)], plain)

    def test_thioxanthone(self):
        self.assertEqual(hashlib.sha256((self.BD / "thioxanthone_gfn2.xyz").read_bytes()).hexdigest(),
                         "d568ecdbf6b786a60577c43957450244576416b10f93536cb6846f35f9659c1a")
        rows = self.rows("thioxanthone_gfn2.xyz")
        self.assertEqual(Counter(r[0] for r in rows), Counter(C=13, H=8, O=1, S=1))
        self.assertEqual({len(r) for r in rows}, {4})

    def test_psp_valence_counts(self):
        z = {}
        for e in "CHNOS":
            text = (self.BD / "psppar" / f"psppar.{e}.yaml").read_text()
            self.assertIn("Pseudopotential XC: 11", text, e)  # PBE
            z[e] = int(re.search(r"No\. of Electrons: (\d+)", text).group(1))
        self.assertEqual(z, dict(C=4, H=1, N=5, O=6, S=6))
        count = lambda name: sum(z[r[0]] for r in self.rows(name))
        self.assertEqual(count("6a_S1.xyz"), 226)
        self.assertEqual(count("thioxanthone_gfn2.xyz"), 72)


class InputsAndDryRun(unittest.TestCase):
    IN = ROOT / "bigdft" / "inputs"

    def test_index_matches_files(self):
        index = json.loads((self.IN / "index.json").read_text())
        self.assertEqual(len(index), 30)
        self.assertEqual(set(index), {p.stem for p in self.IN.glob("*.yaml")})

    def test_input_settings(self):
        for name, run in json.loads((self.IN / "index.json").read_text()).items():
            text = (self.IN / f"{name}.yaml").read_text()
            self.assertIn(f"hgrids: {run['hgrid']}", text, name)
            self.assertIn(f"rmult: [{run['rmult'][0]}, {run['rmult'][1]}]", text, name)
            self.assertIn(f"ixc: {run['xc']}", text, name)
            triplet = run["state"] == "T1"
            self.assertEqual("nspin: 2" in text and "mpol: 2" in text, triplet, name)
            self.assertEqual("geopt:" in text, run["geopt"], name)
            self.assertEqual(text.count("psppar."), 5 if name.startswith("6a") else 4, name)

    def test_every_input_passed_a_dry_run(self):
        seen = {}
        for d in ("dryrun", "dryrun_pbe0"):
            for name, s in json.loads((ROOT / "bigdft" / d / "dryrun_summary.json").read_text()).items():
                self.assertTrue(s["ok"], name)
                self.assertEqual(s["electrons"], 226 if name.startswith("6a") else 72, name)
                self.assertTrue((ROOT / "bigdft" / d / f"log-{name}.yaml").is_file(), name)
                seen[name] = d
        self.assertEqual(set(seen), set(json.loads((self.IN / "index.json").read_text())))

    def test_pbe0_inputs(self):
        for name, run in json.loads((self.IN / "index.json").read_text()).items():
            text = (self.IN / f"{name}.yaml").read_text()
            self.assertEqual("ixc: PBE0" in text, "pbe0" in name, name)
            self.assertEqual(run["xc"], "PBE0" if "pbe0" in name else "PBE", name)


class Phase1(unittest.TestCase):
    RUNS = ROOT / "bigdft" / "runs"

    def mon(self, name):
        lines = (self.RUNS / name / f"data-{name}" / "geopt.mon").read_text().splitlines()
        self.assertTrue(any("converged" in l for l in lines), name)
        last = [l.split() for l in lines if "GEOPT_SQNM" in l][-1]
        return float(last[3]), float(last[5])

    def test_runs_used_dry_run_inputs(self):
        for st in ("S0", "T1"):
            n = f"tx_{st}_pbe_geopt"
            self.assertEqual((self.RUNS / n / f"{n}.yaml").read_bytes(),
                             (ROOT / "bigdft/inputs" / f"{n}.yaml").read_bytes(), n)
            self.assertIn("Number of MPI tasks                   :  12",
                          (self.RUNS / n / f"log-{n}.yaml").read_text(), n)

    def test_converged_and_adiabatic_gap(self):
        e0, f0 = self.mon("tx_S0_pbe_geopt")
        e1, f1 = self.mon("tx_T1_pbe_geopt")
        self.assertLess(max(f0, f1), 2.0e-4)
        self.assertAlmostEqual(e0, -104.958932176445, places=9)
        self.assertAlmostEqual(e1, -104.868778644431, places=9)
        self.assertAlmostEqual((e1 - e0) * 2625.4996, 236.70, places=2)
        summary = json.loads((self.RUNS / "phase1_summary.json").read_text())
        self.assertEqual(summary["adiabatic_PBE"]["kJ_mol"], 236.7)

    def test_pbe0_single_points(self):
        e = {}
        for st in ("S0", "T1"):
            for g in ("S0", "T1"):
                n = f"tx_{st}_pbe0_at_{g}pbe"
                self.assertEqual((self.RUNS / n / f"{n}.yaml").read_bytes(),
                                 (ROOT / "bigdft/inputs" / f"{n}.yaml").read_bytes(), n)
                log = (self.RUNS / n / f"log-{n}.yaml").read_text()
                gn = re.findall(r"iter: +\d+, EKS: +\S+, gnrm: +(\S+),", log)
                self.assertLess(float(gn[-1]), 1.0e-5, n)
                self.assertEqual("Total magnetization                 :  2.000000" in log, st == "T1", n)
                e[f"{st}@{g}"] = float(re.findall(r"^ Energy \(Hartree\) +: +(\S+)", log, re.M)[-1])
        kj = lambda x: x * 2625.4996
        self.assertAlmostEqual(kj(e["T1@T1"] - e["S0@S0"]), 260.75, places=2)
        self.assertAlmostEqual(kj(e["T1@S0"] - e["S0@S0"]), 273.64, places=2)
        self.assertAlmostEqual(kj(e["T1@T1"] - e["S0@T1"]), 238.50, places=2)
        cal = json.loads((self.RUNS / "phase1_summary.json").read_text())["calibration"]
        self.assertTrue(cal["PBE0_passes"])
        self.assertAlmostEqual(cal["PBE0_miss_eV"], 0.1384, places=4)

    def test_t1_is_triplet(self):
        log = (self.RUNS / "tx_T1_pbe_geopt/log-tx_T1_pbe_geopt.yaml").read_text()
        self.assertIn("Total magnetization             :  2.000000", log)


class Data(unittest.TestCase):
    def test_table_s1(self):
        rows = list(csv.DictReader((ROOT / "data/table_s1_noe_restraints.csv").read_text(encoding="utf-8").splitlines()))
        self.assertEqual(len(rows), 35)
        self.assertEqual(sum(r["Restraint ID"].endswith("*") for r in rows), 2)

    def test_smiles_matches_build_script(self):
        row = next(csv.DictReader((ROOT / "data/6a_chemotion_molecule_record.csv").read_text(encoding="utf-8").splitlines()))
        smi = re.search(r'SMI = "([^"]+)"', (ST / "build_6a.py").read_text()).group(1)
        self.assertEqual(row["canonical_smiles"], smi)

    def test_target_conversion(self):
        self.assertAlmostEqual(269 / 96.485332, 2.788, places=3)


if __name__ == "__main__":
    unittest.main()
