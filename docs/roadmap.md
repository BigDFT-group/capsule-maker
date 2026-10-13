# Roadmap and decision register

## Implemented local MVP

- Backend-neutral capsule and normalized-memory schemas, version 1.0.
- Abstract adapter contract and a functional local-file adapter.
- Deterministic goal/tag selection with evidence and correction closure.
- Assembly, human summary, content review, integrity checks, export, and safe import.
- Sensitive-record and likely-secret blocking; contradiction reporting.
- Python API, CLI, optional stdio MCP interface, and an installable Agent Skill.
- Workspace-bound local plugin preparation and two model-handover quick starts.
- NumPy Poisson solver, calculated evidence, portable regressions, and a fresh
  receiving process continuing at 256 intervals after source memory deletion.
- Automated behavioral, adversarial, numerical, CLI, and MCP protocol tests.
- Prepared Python test, packaging, wheel-handover, and documentation CI workflows.

No release, remote push, branch protection change, or hosted site deployment has
been performed. The library version is an unpublished `0.1.0` candidate.

## Before the first published version

Confirm repository visibility and license. Review the implementation and threat
boundaries, designate maintainers, adopt contributor requirements, and establish a
private vulnerability-reporting channel. After explicit approval, create the
BigDFT-group repository, push the reviewed implementation, run remote CI, and
configure required review/check protections. Enable documentation hosting only after
hosting approval and verify its actual deployment URL.

The prepared CI matrix covers Python 3.11/3.12/3.13, but only the interpreter
available locally has been exercised during development. Do not claim remote CI
or cross-version success before those checks run.

## Subsequent work

Verify AOM's real interfaces before implementing its adapter. Evaluate Graphiti,
Mem0, Cognee, and Hindsight against the generic adapter contract. Explore
Paper2Agent capabilities and BigDFT/PyBigDFT scientific workflows separately from
this MVP. Test independent LLM agents and environments with a protocol separating
fidelity, traceability, portability, and continuity. Select a meaningful scientific
application separately from the Poisson test.

Consider binary scientific artifacts, pinned environments, signed provenance,
stronger isolated validation, and improved selection only when required by real
handover use cases.

## Decision register

| Decision | State | Rationale or next action |
| --- | --- | --- |
| Repository owner | Confirmed: BigDFT-group | Project-owner instruction |
| Repository name | Proposed: capsule-maker | No repository found during access check |
| Visibility and license | Pending | Required before publication |
| Website source | Implemented: Markdown with MkDocs | Maintained alongside implementation |
| Hosting | Proposed: GitHub Pages | Publication requires approval |
| Contributor rules | Draft; CI prepared | Adopt policy and configure protection after approval |
| Memory backend for MVP | Implemented: local JSON file | Deterministic cycle without external services |
| AOM integration | Planned after API verification | No undocumented interfaces invented |
