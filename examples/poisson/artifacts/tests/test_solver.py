"""Portable stdlib regression tests; also discovered by project pytest."""

import unittest

import numpy as np
from solver import max_error, solve_poisson


class PoissonRegression(unittest.TestCase):
    def test_boundaries_and_correct_sign(self):
        x, u = solve_poisson(32)
        self.assertEqual(u[0], 0.0)
        self.assertEqual(u[-1], 0.0)
        self.assertGreater(u[16], 0)
        # max error ~ pi² h²/12. For n=32 the bound 1e-3 leaves rounding margin.
        self.assertLess(float(np.max(np.abs(u - np.sin(np.pi * x)))), 1e-3)

    def test_second_order(self):
        errors = [max_error(n) for n in (32, 64, 128)]
        # The discrete sine eigenvalue gives ratio 4 + O(h²).
        for coarse, fine in zip(errors, errors[1:]):
            self.assertGreater(coarse / fine, 3.95)
            self.assertLess(coarse / fine, 4.05)

    def test_discrete_equation(self):
        x, u = solve_poisson(64)
        residual = (2 * u[1:-1] - u[:-2] - u[2:]) * 64**2 - np.pi**2 * np.sin(
            np.pi * x[1:-1]
        )
        self.assertLess(float(np.max(np.abs(residual))), 1e-10)

    def test_invalid_grid(self):
        for invalid in (0, 1, -4, 2.5, True):
            with self.assertRaises(ValueError):
                solve_poisson(invalid)
