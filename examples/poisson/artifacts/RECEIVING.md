# Continue the Poisson convergence study

The dimensionless problem is -u''=pi^2 sin(pi x), x in [0,1], with zero
Dirichlet boundaries. The analytical solution is sin(pi x). Read the sign
correction and the numerical evidence in manifest.json and results.json.

After checking integrity and dependencies, review solver.py, consumer.py and
tests/test_solver.py. Explicitly trust these files before running them.

Run bundled regressions with `capsule-maker verify CAPSULE --trust-code`.
Continue at 256 intervals with `python -B consumer.py` from the capsule directory.
The consumer reproduces the saved evidence first, then checks the new grid.

The maximum absolute error should scale as pi^2 h^2/12 to leading order.
Doubling intervals gives an error ratio between 3.95 and 4.05 on these grids.
At 256 intervals require error below 2e-5. Tests check the discrete residual
below 1e-10 at 64 intervals; this includes floating-point elimination error.
These are validation criteria for this smooth manufactured solution, not for
arbitrary right-hand sides or boundary conditions.
