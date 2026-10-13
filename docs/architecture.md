# Implemented architecture

Capsule-Maker separates the memory backend from the research object. Memory
backends own capture and consolidation; Capsule-Maker selects, assembles, reviews,
validates, and transfers their structured output. The capsule format works without
MCP or a source memory service.

```text
Local JSON adapter (implemented) / future backend adapters
                 │
      objective + tags or word overlap
                 │
      evidence + correction closure
                 │
      assemble → inspect → review
                 │
      versioned JSON + ordinary files
                 │
        ZIP export → safe import
                 │
       fresh researcher / agent

CLI, Python API, and MCP tools call the same tested core.
```

## Source layout

```text
src/capsule_maker/
  adapters.py       Abstract adapter and local JSON implementation
  core.py           Selection, assembly, review, transfer, and validation
  cli.py            Command-line interface
  mcp_server.py     Optional local stdio tools; no code execution
  schemas/          Packaged capsule and normalized memory JSON schemas
tests/              Behavioral, numerical, security, and MCP protocol tests
examples/poisson/   Calculated session A and independent session B
skills/             Installable capsule-maker Agent Skill
docs/               Contributor-maintained Markdown website
.github/            Review template and automated checks
```

## Selection and conflicts

`Goal` contains an objective and optional tags. Explicit tags are ORed against
record tags; without tags, selection uses case-insensitive word overlap, excluding
common generic goal words. Selected records include the transitive closure of
references, evidence, superseded decisions, reverse corrections, explicit conflicts,
and alternatives sharing a selected `claim_key`.

This is deterministic selection, not semantic reasoning. Use explicit tags for
precise scope and inspect the summary. Contradictions are reported rather than
arbitrarily resolved. Conflicting records remain inspectable, but approval and
trusted validation require resolving them in the source with explicit history.

## Review and transfer

The manifest contains structured knowledge and provenance. Artifact hashes bind
ordinary files to the content inventory. Review approval binds the objective,
records, dependencies, inventory, and conflict report to a canonical content digest.
Changes after approval invalidate it. The review record is an assertion by the
caller; it is not a digital signature or proof of human review.

Assembly and import stage files in temporary directories before exposing the
completed destination. Export verifies the actual archive through the import path.
Existing outputs are not overwritten. Unknown files, path traversal, symlinks,
nonregular entries, size violations, corruption, and unsupported schemas fail
clearly. See [format](format.md) and [security](security.md).

## Execution boundary

Import and inspection never load Python code. Ordinary verification checks hashes,
references, and declared installed package versions. It does not install dependencies.
Only `verify_capsule(..., trust_code=True)` or CLI `--trust-code` runs bundled
unittest regressions, in a disposable copy with a timeout. This is not a sandbox.
MCP does not expose execution or approval.

The only implemented adapter is local JSON. [Integration design](integrations.md)
describes what future backend adapters must provide without inventing AOM APIs.
