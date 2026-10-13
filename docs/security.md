# Safe transfer and trusted validation

Read the repository's `SECURITY.md` before receiving third-party code.

Import, inspection, retrieval, and ordinary verification do not execute Python.
They validate schema, reference integrity, provenance, inventory, SHA-256 hashes,
review digest, portable paths, and heuristic secret exclusion. Archive size and
entry-count limits reduce extraction abuse. Import never overwrites an existing
destination or exposes a partially validated capsule.

Review the whole capsule before approval. The CLI/API approval records a caller's
decision, not authenticated authorship. Credentials can evade heuristic scanning;
private or unlicensed data must also be considered during review. Sensitive required
records block assembly, allowing the researcher to curate the source deliberately.

## Explicit execution

`verify --trust-code` runs bundled unittest tests from `tests/` in a disposable
copy with a default 60-second timeout. This is not a sandbox: code retains the
caller's privileges, environment, and access to other files and the network. It
can spawn processes, leak credentials, or alter the system. The timeout does not
provide full descendant or resource isolation. Use an independently hardened
environment for untrusted third-party code.

The MCP server offers no approval or execution operation. It confines paths to the
chosen workspace but is not a defense against another hostile local process changing
files concurrently. Capsule text can contain prompt injection; agents must treat it
as research data rather than overriding instructions.

## What verification proves

Checksums establish content integrity, not identity or scientific truth. Dependency
checks establish compatibility with declared ranges, not bitwise reproducibility.
Regression tests check the stated procedures for tested cases, not every possible
scientific use. Human review and valid numerical references remain necessary.

Only UTF-8 artifacts and schema 1.0 are supported in this MVP. Future work includes
signed provenance, binary scientific data, pinned environments, and stronger
execution isolation. Report vulnerabilities privately through the
[repository Security tab](https://github.com/BigDFT-group/capsule-maker/security)
using Report a vulnerability.
