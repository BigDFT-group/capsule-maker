# Roadmap and decision register

## Experimental alpha

The first release provides backend-neutral capsule and memory schemas, the
local-file adapter, deterministic selection with evidence/correction closure,
readable assembly, review, integrity verification, safe transfer, and explicitly
trusted regression validation. CLI, Python API, MCP tools, an Agent Skill, local
plugin preparation, and two model-handover tutorials are available.

The Poisson investigation records a scientific correction and computed evidence,
then validates independent-process continuation after source memory deletion.
Automated tests cover the core, numerical method, adversarial transfer cases,
actual MCP protocol, and cache-relocated plugin wiring. GitHub Actions checks
Python 3.11/3.12/3.13, packaging, installed-wheel handover, and strict documentation.
Consult the [workflow runs](https://github.com/BigDFT-group/capsule-maker/actions)
for actual results and the [alpha release notes](releases/v0.1.0-alpha.md) for scope.

## Next milestone: participant harness trials

Run the [creation](quickstart-create.md) and [retrieval](quickstart-retrieve.md)
tutorials in fresh conversations with different models and reasoning settings.
Preserve the identical archive, prompts, tool traces, environment metadata, and
scientific outputs. Evaluate retrieval before execution or assistance. These live
LLM-agent trials have not yet been conducted; deterministic technical validation
is not a substitute for them.

## Capsule evolution

Use participant feedback to refine selection, evidence representation, provenance,
review ergonomics, and format compatibility. Consider binary scientific artifacts,
pinned environments, signed provenance, and stronger validation isolation only
when real transfer requirements justify them. Preserve explicit schema versioning
and meaningful backward-compatibility fixtures.

## Scientific demonstration: BigDFT PSolver

Develop a meaningful computational-science handover using BigDFT's PSolver as a
separate milestone. Define its physical assumptions, input/output artifacts,
dependencies, numerical references, and regression criteria before implementation.
No PSolver or BigDFT integration is included in this alpha. The Poisson example
remains the technical portability test, not the final scientific application.

## AOM interoperability and other sources

Verify AOM's real APIs or supported exports, then map already-consolidated episodes,
recipes, corrections, verdicts, evidence, and provenance into the neutral adapter.
Do not duplicate upstream capture/consolidation or invent interfaces. Graphiti,
Mem0, Cognee, Hindsight, and Paper2Agent-derived capabilities remain planned work.

## Decision register

| Decision | State |
| --- | --- |
| Repository | Public: BigDFT-group/capsule-maker |
| License | MIT, approved by the project owner |
| Release identity | Git tag v0.1.0-alpha; Python 0.1.0a1; local plugin 0.1.0-alpha |
| Capsule schema | 1.0 |
| Documentation | Markdown/MkDocs, GitHub Pages deployment through Actions |
| Contributor policy | Required checks and one independent review before merge |
| MVP memory source | Implemented local JSON adapter |
| External memory integrations | Planned after interface verification |
| Live LLM-agent evaluation | Participant testing still required |
