"""Centered differences for -u'' = pi**2 sin(pi*x) on [0,1], u(0)=u(1)=0."""

import numpy as np


def solve_poisson(intervals: int):
    """Return grid and solution, including zero Dirichlet boundary values.

    `intervals` is the number of equal subintervals, so h=1/intervals.
    Solve the symmetric tridiagonal system (2,-1,-1)u = h² f using
    Thomas elimination in O(n) work and memory. Coordinates and u are dimensionless.
    """
    if (
        isinstance(intervals, bool)
        or not isinstance(intervals, (int, np.integer))
        or intervals < 2
    ):
        raise ValueError("intervals must be an integer >= 2")
    x = np.linspace(0.0, 1.0, intervals + 1)
    h = 1.0 / intervals
    rhs = h * h * np.pi**2 * np.sin(np.pi * x[1:-1])
    diagonal = np.full(intervals - 1, 2.0)
    for i in range(1, intervals - 1):
        factor = -1.0 / diagonal[i - 1]
        diagonal[i] += factor
        rhs[i] -= factor * rhs[i - 1]
    interior = np.empty(intervals - 1)
    interior[-1] = rhs[-1] / diagonal[-1]
    for i in range(intervals - 3, -1, -1):
        interior[i] = (rhs[i] + interior[i + 1]) / diagonal[i]
    u = np.zeros(intervals + 1)
    u[1:-1] = interior
    return x, u


def max_error(intervals: int) -> float:
    x, u = solve_poisson(intervals)
    return float(np.max(np.abs(u - np.sin(np.pi * x))))
