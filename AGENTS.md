# Capsule-Maker contributor instructions

Read docs/quality.md and SECURITY.md when changing implementation. Preserve the
backend-neutral format and keep capture/consolidation in upstream memory systems.
Never present planned AOM, Graphiti, Mem0, Paper2Agent, or BigDFT integrations as
working. Do not execute imported code during inspection or import.

For implementation changes run meaningful pytest tests, python -m build, and
python -m mkdocs build --strict with the dev dependencies installed. Update
user-facing documentation alongside behavior. Scientific tests must state and
justify reference values and tolerances; preserve correction history and evidence.
Do not weaken scientific criteria merely to obtain a passing test.

Remote publication, releases, hosting deployment, and repository protection changes
require explicit project-owner approval. The project is licensed under MIT;
license changes require explicit project-owner approval. Supplied PDF/DOCX reference material remains local and
ignored by Git pending redistribution permission.
