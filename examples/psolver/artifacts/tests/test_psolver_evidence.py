"""Portable evidence and charge regressions; these do not rerun compiled PSolver."""

import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1] / "psolver"
sys.path.insert(0, str(ROOT))
from periodic import prepare_charge
from validation import validate_results


class PSolverEvidence(unittest.TestCase):
    def test_recorded_results_and_failed_normalization(self):
        validate_results(
            json.loads((ROOT / "results.json").read_text()),
            json.loads((ROOT / "settings.json").read_text()),
        )

    def test_charge_convention_and_neutrality(self):
        rho, potential = prepare_charge(24)
        self.assertEqual(potential.shape, (24, 24, 24))
        np.testing.assert_allclose(4 * np.pi * rho, 3 * potential, rtol=3e-16, atol=1e-16)
        self.assertLess(abs(float(rho.sum() * (2 * np.pi / 24) ** 3)), 1e-12)
        self.assertAlmostEqual(float(potential[6, 6, 6]), 1.0, places=14)

    def test_isf_grid_constraint(self):
        for n in (8, 17, True):
            with self.assertRaises(ValueError):
                prepare_charge(n)
