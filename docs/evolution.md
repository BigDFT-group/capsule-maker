# Capsule evolution: C1 → PSolver investigation → C2

This milestone is implemented in the development checkout and awaits review;
it is not part of the published `v0.1.0-alpha` tag. No memory backend or live LLM
is needed. Capsule-Maker consumes curated local records; it does not automatically
consolidate conversations.

## What evolves

C1 contains the validated 1D finite-difference Poisson study. A researcher imports
it, performs a separate 3D periodic PSolver investigation, and creates C2. C2
inherits every C1 record and artifact and adds observations, a failed charge
normalization, its correction, numerical evidence, settings, procedures, and tests.
C1 remains unchanged. A fresh process receives only C2 and retrieves both studies,
reproduces the 1D continuation, and runs PSolver at a new 64³ resolution.

```text
Reviewed C1 → import in workspace B → real PSolver calculations
                                      + curated local records
                                                 ↓
                                     unapproved C2 → review → export
                                                 ↓
                           fresh consumer: both studies + new calculation
```

A child uses [format 1.1](format.md#format-11-lineage-and-external-artifacts).
The parent descriptor records its content identifier, SHA-256 of the exact approved
manifest, and packaged manifest/summary paths. Identical inherited artifact paths
are inventoried once in C2. The embedded parent metadata and inherited files let
C2 verify its lineage without access to C1. `verify-parent` additionally checks an
original C1 when available. This proves internal consistency, not authenticated
ancestry: checksums and asserted approvals are not signatures.

New knowledge needs new IDs and source provenance. New corrections may supersede
inherited decisions; only the inherited record's status changes in the child, and
its exact original remains in the parent snapshot. A changed computational
procedure needs a new path. Contradictory active claims are reported and block
approval. Dependencies accumulate; incompatible requirements are reported by
receiving-environment verification. Deep histories eventually reach existing
file/metadata limits and fail rather than silently discard ancestors.

## Run without compiled PSolver

In the current development checkout, install the dev dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
```

The default suite checks evolution, safe transfer, parent preservation, external
artifact hashes, analytical charge construction, recorded PSolver calibration,
and independent retrieval of C2. The compiled-library integration test is skipped
explicitly. Passing recorded-evidence tests does not mean PSolver ran in that
environment. The original [1D demonstration](demonstration.md) remains runnable.

## Provision the actual standalone library

The tested environment is the existing BigDFT core SDK image, PSolver 1.10,
GNU Fortran 13.3.0, Open MPI 4.1.6, Futile 1.9, and ATlab 1.0:

```bash
docker pull bigdft/core-sdk@sha256:669262a09473586c8b0ed6dd877a19b7791c5b81ad79b84affbe9def5e5aa352
```

Docker must be installed and usable by the caller. The client uses this pinned
image with `--pull=never --network none`, mounts only its calculation directory,
and sets `OMP_NUM_THREADS=1`. Availability of this independently distributed
image is external to Capsule-Maker; there is no automatic download or numerical
fallback. A missing image or library is an actionable failure.

Alternatively, `--backend native` requires a GNU/OpenMPI installation providing
`mpif90`, `gfortran`, `pkg-config psolver`, headers/modules, and
`libPSolver-1.a`. Set `PKG_CONFIG_PATH` to your installed library's pkg-config
directory and ensure its runtime libraries are available. The tested compile
command is:

```bash
mpif90 -O2 -fopenmp -I"$(pkg-config --variable=includedir psolver)" \
  psolver_periodic.f90 -o psolver_periodic $(pkg-config --cflags --libs psolver)
```

Native execution is supported by the client but has not been separately validated
on the development host, which has no Fortran compiler. Compiler/MPI portability
beyond this GNU/OpenMPI environment is not claimed. The public Fortran API was
checked against local upstream source at revision
`1c8818b8b65eab0068091cd90de168ab5afe1f40`, particularly
`psolver/src/createKernel.f90`, `PSolver_Main.f90`, and Futile's
`src/f_lib_highlev.f90`. This audit revision is not asserted to be the source
revision of the installed image; actual library/image/source hashes are recorded
in results. The original MIT client calls verified interfaces; GPL PSolver and its
compiled environment remain independently installed, not embedded in capsules.

## Execute the complete scientific handover

Choose a new output directory. This explicitly authorizes execution of the known
local demonstrator's code and compiled PSolver client:

```bash
.venv/bin/python examples/psolver/demo.py \
  --backend docker --output /tmp/capsule-evolution
CAPSULE_PSOLVER_BACKEND=docker .venv/bin/python -m pytest -q -m psolver
```

The demo computes C1, reviews the known deterministic fixture, exports/imports it
in research workspace B, runs PSolver, validates fixed criteria, curates new memory,
extends C1 into C2, and tests/exports C2. It verifies C1's bytes are unchanged,
deletes both source-memory directories, copies only C2 into a fresh directory,
and launches an independent process to import and continue. C1 remains preserved
in the author workspace. Process/workspace separation demonstrates research
independence; it is not an OS access-control sandbox.

Outputs include `C1/`, `C1.zip`, `research-b/C2/`, `C2.zip`,
`psolver-raw-audit.zip`, `fresh-receiver/C2/`, and `report.json`.
The report contains measured sizes, differences, runtime fingerprints, all grid
errors, inherited 1D continuation, and the new 64³ result. The known-fixture review
is programmatic; participants must review their own selected content before approval.

## Scientific problem and frozen criteria

In a periodic cube of side `2π` bohr, choose
`V(x,y,z)=sin(x)sin(y)sin(z)`. PSolver's atomic-unit equation is
`-∇²V=4πρ`, so `ρ=3V/(4π)`. Sample `[0,2π)` without duplicating the periodic
endpoint. The density is neutral, and the potential is defined up to a constant;
compare after subtracting its mean. The Hartree energy is
`½∫ρV d³x = 3π²/8`, since each integral of `sin²` is `π`.

Verified API details matter: `H_potential` overwrites its `rhopot` density argument
with the potential; `pot_ion` is ignored when `sumpion` is false. Interpolating
scaling-function order 16 is selected with zero screening, CPU execution, one MPI
rank and one thread. The exploratory 8³ grid was rejected as too small for ISF16;
PSolver's Fortran STOP returned zero without output. The client therefore checks
output existence, shape, and finiteness as well as process status. The supported
grid sizes are multiples of eight at least 16.

Measured calibration in the pinned image:

| Grid | Maximum potential error | Absolute Hartree-energy error |
| --- | ---: | ---: |
| 16³ | 1.320 × 10⁻¹² | 4.891 × 10⁻¹² |
| 24³ | 2.665 × 10⁻¹⁵ | 7.105 × 10⁻¹⁵ |
| 32³ | 7.772 × 10⁻¹⁶ | 2.665 × 10⁻¹⁵ |
| 48³ | 1.110 × 10⁻¹⁵ | 1.688 × 10⁻¹⁴ |
| 64³, receiving process | 1.221 × 10⁻¹⁵ | 1.199 × 10⁻¹⁴ |

`examples/psolver/calibration.json` retains the actual measured evidence and
runtime fingerprints; each real demo creates its own measurements. Versioned
`settings.json` fixes maximum potential error ≤ `2e-11`, energy error ≤ `1e-10`,
charge integral and potential mean ≤ `1e-12`. These bounds retain about ten
significant digits while allowing cross-build roundoff above the measured errors.
Refinement from 16³ to 24³ must reduce potential error at least tenfold. We do not
require monotonic errors after roundoff is reached or apply the 1D stencil's
second-order rule to PSolver's ISF kernel.

The deliberately wrong `ρ=3V` produces potential error `4π−1 ≈ 11.56637` and
energy larger by `(4π)²`; tests check both. A failed numerical criterion or missing
result stops capsule generation. This single smooth Fourier mode is a validation
case, not a general accuracy/performance assessment or the final hackathon problem.

## API, CLI, and agent workflow

```python
from capsule_maker import Goal, LocalFileAdapter, extend_capsule, compare_capsules

child = extend_capsule("C1", LocalFileAdapter("session-b/memory.json"),
                       Goal("Add periodic PSolver study", ("psolver",)), "C2")
print(compare_capsules("C1", "C2"))
```

```bash
capsule-maker extend C1 session-b/memory.json C2 \
  --goal "Add the periodic investigation" --tag psolver
capsule-maker compare C1 C2
capsule-maker verify C2
capsule-maker verify-parent C2 C1
capsule-maker contents C2 --path SUMMARY.md
# Review the records, provenance, evidence, procedures, dependencies, and tests.
capsule-maker approve C2 --reviewer YOUR_ID
capsule-maker export C2 C2.zip
capsule-maker import C2.zip restored-C2
capsule-maker resume restored-C2
```

The [MCP server and Skill](interfaces.md) expose extension and comparison. An agent
can supply normalized records through the local adapter; this is not conversational
consolidation. C2's `psolver/RECEIVING-PSOLVER.md` describes explicit reruns.
`verify --trust-code` runs inherited 1D regressions and portable charge/evidence
tests, **not compiled PSolver**. The optional integration test and full demo execute
the actual library. No import, inspection, comparison, or ordinary verification
executes bundled code or automatically installs software.

## Capsule size and external artifacts

One measured run produced C1 of 13,563 bytes (6,175-byte ZIP) and C2 of
54,848 bytes (21,471-byte ZIP), while the optional raw audit ZIP was 1,210,815 bytes.
Formatting, provenance, and review timestamps can change these exact sizes; use
`capsule-maker size C1`, `capsule-maker size C2`, and `report.json` for your run.
Large charge/potential arrays, full logs, executables, and environments are not
embedded in the lightweight capsule. C2 includes a compact result table and the
code/settings needed to regenerate the calculation.

The raw ZIP is linked by a manifest descriptor with SHA-256, byte length, URI,
dependencies, and `required_for_reproduction: false`. The demonstrator uses a
content-addressed `urn:sha256:...`, avoiding machine-specific file paths; resolve
it yourself from the named output archive. To check its actual bytes:

```bash
capsule-maker verify-external C2 psolver-raw-audit psolver-raw-audit.zip
```

External files may be binary. They are never fetched, unpacked, or executed by
this operation. Ordinary verification reports them as **not checked**. If a
capsule declares an external artifact essential, integrity success does not mean
that artifact is available; resolve and hash it before claiming reproduction.
Dependencies in external descriptors are informational software requirements,
not automatically checked installed Python distributions.

Unchanged inherited paths appear once per child; copies between standalone
capsules are deliberate. There is no cross-capsule object store or automatic
deduplication of differently named files. A fully reproducible archival deposit
must additionally retain resolved external artifacts, the separately licensed
compiled environment/image, and environment provenance. Capsule-Maker does not
assemble or attest that complete environment archive.


The [capsule gallery](capsules/psolver-periodic-v1/index.md) provides the frozen
C1/C2 downloads and a knowledge description. Use the [agent reuse prompts](reuse-psolver.md)
for a fresh-session retrieval, critique, and explicitly trusted continuation trial.
