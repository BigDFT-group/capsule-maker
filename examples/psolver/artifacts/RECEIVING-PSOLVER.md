# Continue the periodic study

Review `psolver/results.json`, `settings.json`, `periodic.py`, `validation.py`,
and `psolver_periodic.f90`, plus the parent snapshot. Charge is in atomic units:
`rho=3*sin(x)*sin(y)*sin(z)/(4*pi)`, not the mathematical right hand side.
The periodic solution is compared after subtracting its mean. `H_potential`
overwrites the density with the potential. ISF order 16 requires these grids
at least 16 and divisible by eight; the 8-cubed attempt was rejected by PSolver.

`capsule-maker verify CAPSULE --trust-code` explicitly executes the original 1D
regressions and the recorded-evidence/charge tests. It does NOT compile or rerun
PSolver. For a real new computation, explicitly trust the client and provision
PSolver using the evolution documentation. Run, with a NEW output directory:

    python psolver/periodic.py --backend docker --work /tmp/psolver-next

This reruns the four-grid study and the rejected-normalization control using
actual PSolver; `--backend native` requires the documented GNU/OpenMPI installation.
Use the Python `compile_solver` and `run_case` functions for a new 64-cubed grid.
The original 1D `consumer.py` can still continue its 256-interval study.
The optional raw archive is a checksum-linked audit artifact, never fetched
or executed automatically; the compiled library/image remains separately installed.
