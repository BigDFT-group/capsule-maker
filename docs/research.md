# Capsule-Maker for reproducible AI-assisted science

*Research paper overview based on the hackathon one-page summary and the
repository demonstrations.*

The hackathon summary credits Giuseppe Fisicaro, Tengxiang Li, Louis Beal,
Yoann Curé, and Luigi Genovese.

## Abstract

Scientific agents generate decisions, corrections, numerical results and working
procedures across long sessions. These findings are difficult to transfer to
another researcher or agent when the evidence and rationale are scattered through
conversation histories. Capsule-Maker curates structured research records into a
portable object whose claims, evidence and procedures can be inspected together.
A Git repository lets collaborators extend the capsule through reviewable
contributions. A single release ZIP supports both an offline Git restoration and a
Git-free scientific handover.

## Method

A memory adapter supplies records, supporting files and provenance. Capsule-Maker
selects records for a stated goal, preserves dependencies and correction links, and
reports conflicts for review. A receiving agent can inspect the resulting
manifest, read evidence and resume through the CLI or through the local MCP
interface on a restored capsule. The Agent Skill describes the review and
continuation procedure. Capture and consolidation belong to upstream systems.
AOM and other external memory adapters remain planned.

Scientific lineage identifies the capsule that an investigation extends and
retains superseded decisions and their evidence. Git history records changes to
the working files and enables branches and pull requests. The
[release envelope](git-releases.md) binds a capsule snapshot and its accompanying
Git bundle to an identified revision through release metadata and checksums.

## Observations and evaluation

The [Poisson demonstration](demonstration.md) transfers a validated 1D solver,
including the rejected sign convention, its correction and evidence of
second-order convergence. The [PSolver continuation](evolution.md) inherits
that knowledge, records a separate normalization correction, and demonstrates a
new periodic 3D computation in a separate receiving process. The Git-backed
example restores the same C2 content with and without Git. These checks assess
reproducible transfer on known fixtures.

The concept note proposes four questions for broader evaluation:

- **Fidelity.** Can a receiver distinguish the accepted method from a rejected one?
- **Traceability.** Can a receiver cite the supporting record and artifact?
- **Portability.** Can the receiver work without the original memory backend?
- **Continuity.** Can the receiver choose and carry out a defensible next step?

The [reuse protocol](reuse-psolver.md) gives separate prompts for unaided
retrieval and authorized scientific continuation. Comparative studies across
harnesses, models and a baseline without the capsule require their own controls.
Integrity checks establish consistency of the transferred files. Scientific
validity requires evidence and domain review.

## Hackathon case study: knowledge transfer and growth

The hackathon team studied photocatalytic peptide 6a from
[Irle and colleagues](https://doi.org/10.1038/s44160-026-01173-7). The reported
experimental triplet energy is 269 kJ/mol. The team used
[Paper2Agent](https://doi.org/10.1038/s41586-026-11044-y) to create a paper skill
and prepared a [BigDFT](https://doi.org/10.1063/5.0004792) workflow with
dry-run checks informed by [LARA-HPC](https://doi.org/10.1103/cp6v-t93q).
These were tools used in the study.

The summary reports that Claude Code created a starting capsule with 63 records
and an archive size of approximately 1.19 MB. Fresh Claude Code and OpenCode
sessions, using Claude Opus 5.5 and local Qwen respectively, recovered the
research goal and produced matching thioxanthone calibration inputs and a PBE
triplet gap of 241.21 kJ/mol. The OpenCode session also drew on a separate
BigDFT runtime capsule of about 28 kB.

Both sessions produced new PBE0 peptide inputs with the same physical model at
the shared grid. The summary reports an input comparison for that step. The
Claude continuation also exported an enriched capsule with 88 records, adding
25 records of results and corrected procedures. Its constrained adiabatic PBE
triplet gap for peptide 6a was 227.05 kJ/mol. The calculation fixed 55 atoms and
omitted solvent and zero-point corrections. The computed value differs from
the reported experimental value.

The case study provides examples of cross-harness transfer, reuse of a separate
runtime capsule, and the growth of a research record. The Poisson → PSolver
release illustrates the new Git distribution workflow separately. See the
[hackathon artifacts](https://github.com/BigDFT-group/capsule-maker/tree/main/Open-Scientific-Intelligence-Hackathon-2026)
for the recorded investigations.

## Materials

Start with the [downloadable scientific example](capsules/psolver-periodic-v1/index.md),
then follow the [creation](quickstart-create.md) and
[retrieval](quickstart-retrieve.md) tutorials for your harness.
The [hackathon presentation video](https://github.com/BigDFT-group/capsule-maker/blob/main/Open-Scientific-Intelligence-Hackathon-2026/media/capsule_maker_video_good_v2.mp4)
is available in the repository.
