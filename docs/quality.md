# Contributor quality requirements

These requirements apply equally to maintainers, external contributors, and
AI-assisted contributions. Automation and
review have distinct responsibilities; passing CI alone does not establish
scientific correctness.

## Definition of done

| Area | Requirement | Evidence and enforcement |
| --- | --- | --- |
| Behavior | Implement usable behavior within the agreed scope | Reviewer runs or assesses the documented example |
| Tests | Cover changed behavior and meaningful failure modes | Required pytest CI checks |
| Scientific validation | Specify assumptions, units, boundaries, error norms, and tolerances | Numerical tests plus scientific review |
| Provenance | Link verified claims to inspectable evidence; label hypotheses and unresolved claims | Schema checks and review |
| Corrections | Preserve superseded decisions and their correction links | Round-trip and reference-integrity tests |
| Portability | Essential operations work without the source memory service | Separate-process handover test |
| Safe transfer | Reject unsafe archive paths, detect integrity failures, and keep inspection free of code execution | Adversarial import tests |
| Sensitive content | Exclude credentials and designated sensitive records before export | Filter tests and content review |
| Compatibility | Keep a versioned schema; document migrations or breaking changes | Schema fixtures and release review |
| Documentation | Update user instructions and examples with changed behavior | Strict documentation build and reviewer checks |
| Maintainability | Keep interfaces small, dependencies justified, and errors actionable | Code review |
| Licensing | Contributions and included artifacts must have compatible redistribution rights | Contributor declaration and review |

Avoid tests that merely mirror the implementation. Scientific tolerances must be
justified before accepting numerical output; do not relax them simply to make a
failing test pass. External backend tests may be optional, but the local portable
cycle must run without credentials or external services.

## Merge policy

All changes enter through a pull request with passing required checks and resolved
review conversations. During the initial single-maintainer phase, the project
owner reviews and authorizes merges; a separate approving reviewer is not required.
GitHub is configured with zero required approvals and no last-push approval
requirement, so the sole contributor can merge their own PR after CI passes.
This exception was explicitly approved by the project owner because an independent
reviewer is not yet available. It does not reduce scientific validation criteria.

Required checks apply to administrators; routine bypass permissions are excluded.
Force pushes and deletion of the protected main branch remain prohibited. When
additional maintainers are available, restore one independent approving reviewer,
fresh approval after substantive changes, and last-push approval through a
reviewed, project-owner-authorized protection update. Seek qualified scientific
review when available, and document validation limitations in the meantime.

Required checks are `python-tests-3.11`, `python-tests-3.12`, `python-tests-3.13`,
`packaging`, and `documentation`. They check the portable cycle, installed package,
and strict documentation build. The publication workflow applies branch protection
only after the initial main branch and these checks succeed. Branch protection is
an actual GitHub setting, not an effect of committing this file; consult repository
settings and workflow runs for its operational state.

Documentation-only changes require a strict documentation build and content
review; they do not require unrelated scientific tests. Exceptions need a recorded
reason and maintainer agreement rather than an undocumented bypass.

## Review checklist

- Is the problem and resulting behavior clear?
- Are tests meaningful, reproducible, and adequate for the changed risk?
- Can a receiving researcher interpret evidence and reproduce the stated result?
- Have schema, user instructions, and examples changed together where needed?
- Is imported code executed only after explicit authorization?
- Are credentials, private data, and unlicensed artifacts excluded?
- Are unsupported integrations and limitations described honestly?

## Evolving these requirements

Policy changes use the same pull-request review process. Explain the problem,
impact on contributors, and enforcement mechanism. Changes to scientific criteria
or format compatibility need a reviewer competent in the affected area. Specific
maintainers and code owners will be designated when the team is established.
