# Capsule-Maker

**Portable Research Memory for Reproducible AI-Assisted Science**

An experimental alpha for the Open Scientific Intelligence Hackathon,
21–22 October 2026.

[Repository](https://github.com/BigDFT-group/capsule-maker) ·
[Documentation](https://bigdft-group.github.io/capsule-maker/) ·
[Alpha release](https://github.com/BigDFT-group/capsule-maker/releases/tag/v0.1.0-alpha)

Deterministic technical handover is validated. Live LLM-agent retrieval across
models remains an experiment for participants.

AI research agents accumulate decisions, corrections, evidence, and useful code.
Capsule-Maker selects that knowledge for an explicit goal and packages a readable,
versioned research object that another researcher can inspect and continue without
the original conversation or memory service.

AOM and other memory systems remain responsible for capture and consolidation.
Capsule-Maker handles goal selection, reference closure, review, validation, and
transfer. **The only implemented backend is the local JSON-file adapter.**

## Development milestone: capsule evolution

The current review checkout adds immutable C1 → C2 extension, parent–child
provenance, comparison, external-artifact checksums, and an optional standalone
BigDFT PSolver 3D periodic demonstration. These additions are **unreleased** and
not included in `v0.1.0-alpha`. See [the evolution tutorial](docs/evolution.md)
for the verified Fortran API, pinned execution environment, criteria, and sizes.
The [capsule gallery](docs/capsules/psolver-periodic-v1/index.md) contains frozen
C1/C2 archives and knowledge descriptions; [agent reuse prompts](docs/reuse-psolver.md)
separate retrieval, critique, and trusted scientific continuation.
Default pytest remains independent of compiled PSolver. In this development
checkout with dev dependencies and the documented image installed:

```bash
.venv/bin/python examples/psolver/demo.py --backend docker --output /tmp/capsule-evolution
CAPSULE_PSOLVER_BACKEND=docker .venv/bin/python -m pytest -q -m psolver
```

A fresh process receives C2, retrieves both investigations, reproduces the 1D
continuation, and computes a new 64³ PSolver result. The only memory adapter remains
local JSON; this scientific client is not a general BigDFT integration.

## Install

Python 3.11 or newer. Clone the tagged experimental version:

```bash
git clone --branch v0.1.0-alpha https://github.com/BigDFT-group/capsule-maker.git
cd capsule-maker
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[science,mcp]'
.venv/bin/capsule-maker --help
```

Use `-e '.[dev]'` instead for tests, package builds, and documentation. Core runtime
dependencies are jsonschema and packaging; NumPy and the official MCP SDK are
optional extras. No LLM account or memory-service credentials are needed.

## Try it in your agent harness

Follow the [creation quick start](docs/quickstart-create.md) to prepare and install
a local plugin and paste the creator prompt into a fresh conversation. Then use
the [retrieval quick start](docs/quickstart-retrieve.md) with another model and only
the exported archive. Both pages separate inspection from review and trusted code
execution. The receiving prompt does not include the scientific answer key.

`capsule-maker prepare-plugin --workspace PATH --marketplace NAME` prepares the
workspace-bound Skill/MCP bundle and local catalog; installation into the harness
is a separate explicit step. No public plugin catalog is assumed.

## Run the complete handover

Choose a new output directory:

```bash
.venv/bin/python examples/poisson/demo.py --output /tmp/capsule-poisson-demo
```

Session A computes a NumPy finite-difference solution of `-u'' = π² sin(πx)` with
zero boundaries. It records an incorrect sign choice, the correction, calculated
evidence at 32/64/128 intervals, and regression tests. The demo creates, approves,
checks, and exports a capsule; deletes the source memory and original capsule;
then starts a separate receiving process to import, test, and continue at 256
intervals. The receiving process needs the installed library and NumPy, not the
source memory. This is process-level research independence, not an OS sandbox.

Expected output includes maximum error approximately `1.255e-5`, convergence ratio
approximately `4.00009`, and `source_memory_deleted_before_consumer: true`.
The demo's approval applies to this known local fixture; general transfers require
actual content review.

## Create and review a capsule yourself

```bash
.venv/bin/python examples/poisson/session_a.py /tmp/poisson-memory
.venv/bin/capsule-maker create /tmp/poisson-memory/memory.json /tmp/poisson-capsule \
  --goal "Continue the numerical convergence study" --tag convergence
.venv/bin/capsule-maker inspect /tmp/poisson-capsule
.venv/bin/capsule-maker contents /tmp/poisson-capsule --path SUMMARY.md
```

Read the selected knowledge, evidence, procedures, dependencies, and tests. Then
record an actual review decision:

```bash
.venv/bin/capsule-maker approve /tmp/poisson-capsule --reviewer "YOUR_REVIEWER_ID"
.venv/bin/capsule-maker export /tmp/poisson-capsule /tmp/poisson-capsule.zip
.venv/bin/capsule-maker import /tmp/poisson-capsule.zip /tmp/poisson-restored
.venv/bin/capsule-maker verify /tmp/poisson-restored
.venv/bin/capsule-maker resume /tmp/poisson-restored
```

Import, inspect, retrieve, and ordinary verification **never execute capsule code**.
Only after explicitly trusting the included Python files:

```bash
.venv/bin/capsule-maker verify /tmp/poisson-restored --trust-code
.venv/bin/python -B /tmp/poisson-restored/consumer.py
```

Trusted tests run with your OS privileges in a disposable copy. This is not a
sandbox. Checksums prove integrity, not authorship or scientific validity.
See [security and limitations](SECURITY.md).

## Python API

```python
from capsule_maker import Goal, LocalFileAdapter, create_capsule, inspect_capsule

manifest = create_capsule(
    LocalFileAdapter("memory.json"),
    Goal("Continue convergence", ("convergence",)),
    "new-capsule-directory",
)
print(inspect_capsule("new-capsule-directory")["records"])
```

The same library provides `approve_capsule`, `export_capsule`, `import_capsule`,
`verify_capsule`, `retrieve_content`, and `resume_knowledge`. Errors raise
`CapsuleError`; CLI failures exit with status 2.

## Architecture and format

```text
Memory adapter → deterministic goal selection + dependency closure
               → assemble → inspect → review → ZIP export
               → safe import → integrity/environment verification
               → explicitly trusted scientific continuation
```

Capsules contain `manifest.json`, `SUMMARY.md`, and ordinary UTF-8 files. The
manifest holds schema version `1.0` (roots from legacy memory) or `1.1` (evolution),
origin, goal, selected records, provenance,
dependencies, conflicts, review digest, and a SHA-256 content inventory. Verified
claims require packaged evidence; corrections retain superseded decisions.
Selection uses ORed explicit tags, or word overlap when tags are omitted.
Contradictions are reported and block approval.

Schemas ship inside the Python package under `src/capsule_maker/schemas/`.
See the [format reference](docs/format.md), [adapter contract](docs/integrations.md),
and [architecture](docs/architecture.md).

## MCP and Agent Skill

```bash
.venv/bin/capsule-maker-mcp --workspace /ABSOLUTE/PATH/TO/RESEARCH_WORKSPACE
```

Configure this command as a stdio server in your MCP client. Tools create, inspect,
list/retrieve content, verify without execution, retrieve resume knowledge, export
already-approved capsules, and import archives. The development version also
extends capsules and compares versions. Paths are workspace-relative.
The server also serves `capsule://NAME/summary`. Approval and execution are not
exposed through MCP.

Copy the complete `skills/capsule-maker` directory into your agent host's skill
location. Its `SKILL.md` describes implemented CLI/API behavior and trust limits.
See [MCP and Skill usage](docs/interfaces.md).

## Tests, packaging, and website

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m build
.venv/bin/python -m mkdocs build --strict
.venv/bin/python -m mkdocs serve
```

GitHub Actions checks Python 3.11/3.12/3.13 tests, a wheel/sdist build,
wheel-installed handover/plugin setup, and strict documentation builds.
Documentation deploys to GitHub Pages after merges to main. See the actual
[workflow runs](https://github.com/BigDFT-group/capsule-maker/actions) for current
results. Contributors maintain Markdown in `docs/` through reviewed changes;
see [contributing](CONTRIBUTING.md).

## Limits and next steps

The development implementation supports UTF-8 packaged artifacts, explicit
schema 1.0/1.1 compatibility, optional external binary-data references, heuristic secret detection,
explicitly declared contradictions, and deterministic selection. It does not
understand arbitrary natural-language contradictions, authenticate reviewers,
sandbox code, or guarantee that an environment is reproducible from version ranges.

AOM integration awaits verification of real upstream interfaces. Graphiti/Mem0
adapters, Paper2Agent-derived capabilities, BigDFT/PyBigDFT workflows, signed
capsules, pinned environments, and independent LLM evaluation are future work.
The Poisson example is a numerical portability test, not the final scientific
hackathon application. Capsule evolution and the standalone PSolver sinusoid are
implemented locally pending review; next steps include participant trials, more
meaningful scientific problems, and verified AOM interoperability. See the
[roadmap](docs/roadmap.md) and [alpha release notes](docs/releases/v0.1.0-alpha.md).

## License

[MIT](LICENSE). Supplied PDF/DOCX reference material is excluded pending
redistribution permission.
