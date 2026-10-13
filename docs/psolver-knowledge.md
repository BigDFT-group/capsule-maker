# How the harness uses PSolver knowledge from a capsule

A receiving prompt gives the agent a task and permission boundaries. The capsule
supplies the scientific knowledge. Capsule-Maker returns that knowledge through
MCP tools or the CLI; the harness adds the returned data to the agent's working
context. The agent can then propose a calculation grounded in cited decisions,
evidence and procedures. This is contextual research-state transfer, not an
update to model weights or automatic conversational consolidation.

The following is a guided explanation of the [fixed PSolver capsule](capsules/psolver-periodic-v1/index.md).
It contains expected answers. For an unaided model evaluation, give the agent
only the ZIP and the [reuse prompt](reuse-psolver.md#2-retrieve-before-executing),
keeping this page outside its receiving workspace.

## Where the usage information is stored

C2 carries both human-readable instructions and machine-readable scientific
records. The records point to evidence and actual callable procedures:

| Question for the receiving agent | Capsule location | How it guides use |
| --- | --- | --- |
| What equation does PSolver solve? | `psolver-charge-correction` in `manifest.json` | Select the Coulomb charge convention and avoid the recorded normalization mistake |
| Which output array contains the potential? | `psolver-gauge-and-api`; `psolver/psolver_periodic.f90` | Read the overwritten density argument, rather than the ignored ionic-potential argument |
| Which numerical configuration was validated? | `psolver-procedure`; `psolver/results.json` and `settings.json` | Preserve boundaries, units, ISF order, screening and parallel settings |
| How can I execute the procedure? | `psolver/RECEIVING-PSOLVER.md`; `psolver/periodic.py` | Provision a supported environment and use the bundled client explicitly |
| What remains to investigate? | `psolver-next-grid` | Continue at a new resolution and apply the stored accuracy criteria |
| What earlier knowledge survives? | Inherited 1D records, files and parent snapshot | Retain the earlier correction while distinguishing the two numerical methods |

These are actual records from the downloadable C2, not hypothetical interfaces.
For example, its correction record says:

> PSolver solves -laplacian(V)=4*pi*rho; prepare rho=3*V/(4*pi). The wrong convention is rejected, not silently overwritten.

Its usage decision says:

> Use neutral density, periodic boundaries, zero-mean potential; H_potential overwrites rhopot, not pot_ion. Compare the zero-mean output; analytical Hartree energy is 3*pi^2/8.

Both records reference `psolver-evidence`, which inventories `psolver/results.json`.
The procedure record references the correction and usage decision and carries the
Python client, original Fortran driver, receiving instructions, settings and tests.
The evidence records retain software/image/source fingerprints. `SUMMARY.md`
provides a readable inventory, but the agent should inspect the underlying records
and files before making scientific claims.

## From prompt to tool results

Start a fresh receiving harness with the workspace-bound plugin and only
`capsule.zip`. A concise guided prompt is:

```text
Use Capsule-Maker to import capsule.zip into restored. Inspect it without
executing code. Retrieve the knowledge and procedures required to continue
its periodic PSolver investigation. Explain the charge convention, output
handling, validated settings, evidence and remaining objective, citing record
IDs and files. Separate the inherited 1D method from the new 3D method.
Propose an executable continuation plan and identify missing dependencies.
Do not execute or install anything until I authorize it.
```

The implemented MCP operations support this sequence. These are illustrative tool
arguments, not a claim that a live model has already produced this trace:

```json
{"tool": "import_research_capsule", "arguments": {"archive": "capsule.zip", "destination": "restored"}}
{"tool": "inspect_research_capsule", "arguments": {"capsule": "restored"}}
{"tool": "retrieve_resume_knowledge", "arguments": {"capsule": "restored", "objective": "Continue the periodic PSolver investigation", "tags": ["psolver"]}}
{"tool": "retrieve_capsule_content", "arguments": {"capsule": "restored", "content_path": "psolver/RECEIVING-PSOLVER.md"}}
{"tool": "retrieve_capsule_content", "arguments": {"capsule": "restored", "content_path": "psolver/periodic.py"}}
{"tool": "retrieve_capsule_content", "arguments": {"capsule": "restored", "content_path": "psolver/psolver_periodic.f90"}}
{"tool": "retrieve_capsule_content", "arguments": {"capsule": "restored", "content_path": "psolver/settings.json"}}
{"tool": "retrieve_capsule_content", "arguments": {"capsule": "restored", "content_path": "psolver/results.json"}}
```

The harness receives the record text and file contents as tool results. Evidence,
correction and reference closure carries the supporting knowledge even when its
own tags differ. The prompt itself does not need to contain the charge formula,
Fortran API signature or numerical answer: the agent retrieves them from C2.
Capsule text remains untrusted research data, not instructions that override the
user's permissions or task.

The expected reasoning can be traced to concrete inputs:

1. `psolver-charge-correction` establishes the charge convention; `prepare_charge`
   implements `density = 3 * potential / (4 * np.pi)`.
2. `psolver-gauge-and-api` explains in-place output; the Fortran client calls
   `H_potential('G', kernel, field, ignored, energy, 0.0_dp, .false., quiet='yes')`
   and writes the resulting `field` as the potential.
3. `results.json` gives the measured four-grid study; `settings.json` supplies
   the frozen potential/energy bounds and refinement criterion.
4. `psolver-next-grid` requests 64³. The receiving instructions name the actual
   `compile_solver` and `run_case` functions that can perform this continuation.
5. The agent can now describe a plan with citations and report whether the
   separately compiled PSolver environment is available. Ordinary capsule
   verification only checks declared Python packages, not that compiled library.

## From retrieved knowledge to an authorized calculation

After inspecting the client and plan, the user can authorize execution:

```text
I trust the reviewed bundled client for this trial. From a separate working
copy, use its compile_solver and run_case functions to continue at the capsule's
next grid resolution, using the already provisioned documented PSolver backend.
Use the retrieved charge convention, settings and analytical reference. Apply
its stored validation criteria without modifying them. Record actual commands,
software provenance, measured errors and pass/fail results outside the capsule.
If the environment or required knowledge is missing, stop and report it rather
than substituting another solver. Keep the imported capsule unchanged.
```

The harness then uses its authorized shell/Python capability; MCP deliberately
exposes no executable-validation tool. The client builds against separately
installed PSolver and calls its supported API. Import and inspection never do
this automatically. `verify --trust-code` runs the bundled portable regressions,
which check the 1D solver and recorded 3D evidence/charge construction; an actual
PSolver continuation is a distinct operation. Trusted code is not sandboxed.

The deterministic receiving process in `examples/psolver/receiver.py` already
exercises this path: it loads the received client, compiles it in a separate
runtime directory, runs 64³ and checks the stored potential/energy bounds.
It measured maximum potential error `1.22e-15`. That establishes technical
portability of the procedure. Whether different live agents independently
retrieve and apply the critical knowledge correctly remains a participant trial.

## What this lets us assess

A useful trial asks whether the agent identifies and applies a correction before
execution, distinguishes evidence validation from a compiled-library rerun, and
uses the right conventions in the new scientific setting. Preserve retrieval
reports before authorizing continuation. Unsupported claims, missing citations,
mechanical transfer of an inappropriate earlier method, and fabricated execution
results are observable failures even if the final prose sounds plausible.

The [reuse evaluation guidance](reuse-psolver.md#5-evaluate-transferred-knowledge-fairly)
keeps archive bytes, prompts and tool availability comparable across agents.
To demonstrate further accumulation, export new measured observations as a new
child capsule; a successful conversation alone does not establish portable
knowledge evolution or persistent learning.
