# A working two-session Poisson investigation

The dimensionless manufactured problem is

```text
-u''(x) = π² sin(πx), x ∈ [0,1]
u(0) = u(1) = 0
Exact solution: u(x) = sin(πx)
```

## Run everything

After installing the science extra or dev dependencies, from the repository root:

```bash
.venv/bin/python examples/poisson/demo.py --output /tmp/capsule-poisson-demo
```

Choose a new destination. The script leaves an exported archive, imported capsule,
and `session-b/continuation.json` for inspection.

## Session A: generate knowledge and numerical evidence

`session_a.py` runs the NumPy tridiagonal solver and calculates maximum absolute
errors at 32, 64, and 128 equal subintervals. Its structured memory records include
the scientific objective, boundary decision, wrong sign, correction, procedure,
evidence, unresolved next grid, a separate hypothesis, and unrelated notes.

For `-u''=f`, the centered operator is `(2u_i-u_(i-1)-u_(i+1))/h²`. The correct
right-hand side is positive. Negating it gives a negative solution and maximum
error greater than 2. This calculated failure is retained as a superseded choice;
the correction links back to it. Evidence includes both the failure and validated
outputs; it is computed rather than invented.

## Selection, review, and export

The `convergence` tag selects the validated procedure and remaining objective.
Reference closure includes the problem, boundary conditions, correction, rejected
choice, and numerical evidence. The unrelated notes and future forcing hypothesis
are not needed and remain outside this capsule.

The demo assembles the capsule, records a review of the known reproducible fixture,
runs its portable regressions, and exports a checksummed ZIP. General source
material requires actual inspection and an explicit reviewer decision.

## Session B: independent continuation

Before starting the receiver, the demo deletes session A's memory directory and
original assembled capsule. A separate interpreter imports the ZIP in a new
receiving directory, checks dependencies, and explicitly runs the packaged tests.
A second subprocess invokes `consumer.py`, which checks the critical knowledge,
reproduces saved evidence, and continues at 256 intervals.

The consumer reads only its imported capsule and installed dependencies. It has
no original conversation or memory store. The subprocess and directory provide
research-state separation; they are not a security sandbox or an OS access policy.
The demo executes only known locally authored fixture code under explicit trust.

## Numerical criteria

For this sine mode the discrete eigenvalue is `4 sin²(πh/2)/h²`, so the amplitude
error is `π²/(4 sin²(πh/2)/h²) - 1 = π²h²/12 + O(h⁴)`. This explains second-order
convergence and an error ratio near four when doubling the intervals.

Portable regressions require maximum error below `1e-3` at 32 intervals, ratios
between `3.95` and `4.05` across 32/64/128, and discrete residual below `1e-10` at
64 intervals. Session B requires maximum error below `2e-5` at 256 intervals and
a ratio in the same interval against 128. It reproduces saved errors within
`1e-11`, allowing floating-point platform differences.

An actual local run produced maximum error `1.254994550148325e-5` at 256 intervals
and ratio `4.0000903515629`. Tests enforce the criteria, not exact platform-specific
last digits. Missing evidence or correction links fail explicitly.

This is a deterministic portability test, not evidence of improved LLM reasoning
or a novel scientific result. A later scientific application will be selected
separately.
