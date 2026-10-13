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

All changes enter through a pull request. Require one approving reviewer other
than the author, passing required checks, resolution of review conversations, and
fresh approval after substantive changes. Apply the same rule to administrators;
exclude routine bypass permissions. Do not permit force pushes or deletion of the
protected main branch.

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
