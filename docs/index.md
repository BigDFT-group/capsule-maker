# Research that travels with its evidence

<div class="project-banner"><span>CAPSULE-MAKER · LOCAL MVP</span><p>Portable Research Memory for Reproducible AI-Assisted Science</p></div>

AI-assisted research produces more than answers: hypotheses, numerical evidence,
reusable procedures, corrected mistakes, and questions still worth pursuing.
Capsule-Maker packages a selected research state so another researcher or
agent can understand it and continue the work without the original conversation
or memory service.

**Open Scientific Intelligence Hackathon · 21–22 October 2026**

## What a receiving researcher should get

| Research need | Capsule content |
| --- | --- |
| Understand the problem | Context, goal, hypotheses, and scope |
| Know what to trust | Claims with explicit status and supporting evidence |
| Avoid repeating mistakes | Corrections linked to superseded decisions |
| Continue the calculation | Functions, dependencies, procedures, and regression tests |
| Assess reproducibility | Provenance, checksums, validation criteria, and environment requirements |

The implemented MVP supports a complete **create → review → export → import →
verify** cycle using a local-file adapter and a separate-process Poisson example.
Import and inspection never automatically execute imported code.

## Try a handover with two models

Start with [Create a capsule](quickstart-create.md), then open a fresh conversation
and follow [Retrieve a capsule](quickstart-retrieve.md). Each page begins with local
plugin installation and contains copy-paste prompts. Use one model to assemble the
capsule and another to recover it, without sharing the original conversation.

## Start contributing

Read the [implemented architecture](architecture.md), follow the
[scientific handover example](demonstration.md), and use the
[contributor requirements](quality.md) to prepare a pull request. The
[documentation guide](contributing.md) explains how to maintain this website.

## How this complements existing projects

AOM already captures episodes, consolidates recipes, records verdicts and
corrections, and exports frozen memories. Capsule-Maker should reuse that research
state through an adapter rather than reimplement those capabilities. Its focus is
a neutral format, goal-based selection, human-readable transfer, secret exclusion,
and portability beyond the source memory system.

The supplied *Capsule-Maker and AOM* document reports development benchmarks with
small counts and incomplete campaigns. It does not establish superiority over a
no-memory baseline or portability across arbitrary agent platforms. Those claims
are outside this project's current evidence.

[Paper2Agent](https://github.com/jmiao24/Paper2Agent) turns papers and associated
code into agent capabilities; those capabilities could later be included with their
provenance and tests. [BigDFT](https://github.com/BigDFT-group),
[BigDFT Agent Skills](https://github.com/BigDFT-group/skills), and
[LARA-HPC](https://github.com/BigDFT-group/llm-hackathon-2025) provide related
scientific workflow experience. These integrations are future work.

[AOM](https://gitlab.com/l_sim/ia_tools/aom), Mem0, Graphiti, Cognee, and Hindsight
are potential memory sources, not runtime requirements for a receiving capsule.

## Current status

The Python library, CLI, local-file adapter, optional MCP server, and Agent Skill
are implemented locally. The deterministic Poisson capsule has been exported,
imported, and continued in a separate process with session A memory deleted.
The proposed repository owner is **BigDFT-group**. Visibility, license, hosting,
and repository protection remain pending approval; nothing has been published.
Consult the [roadmap and decision register](roadmap.md).
