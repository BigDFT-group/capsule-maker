# Research Capsule formats 1.0 and 1.1

The format is a directory of human-inspectable UTF-8 files, optionally transported
as ZIP. It is independent of the producing memory backend and MCP.

```text
manifest.json          Structured metadata, knowledge, provenance, inventory
SUMMARY.md             Human-readable review summary
solver.py              Example computational procedure
consumer.py            Example continuation procedure
tests/test_solver.py   Portable unittest regressions
results.json           Supporting numerical evidence
RECEIVING.md           Receiving researcher instructions
```

See the [generated example manifest](example-manifest.json). It is an illustrative
manifest from the actual Poisson generator, not a standalone capsule: its artifacts
are produced by the executable example. The schemas are packaged as
`capsule_maker/schemas/capsule-v1.schema.json` and `memory-v1.schema.json`.
Python callers can obtain them with `capsule_maker.core.schema()` and
`schema("memory")` using installed package resources.

## Manifest fields

| Field | Meaning |
| --- | --- |
| `schema_version` | `1.0` or `1.1`; unsupported versions are rejected |
| `origin` | Backend identifier and descriptive source context |
| `goal` | Research objective and explicit selection tags |
| `records` | Selected scientific knowledge, with statuses and relationships |
| `sources` | Stable provenance IDs, source URIs, and descriptions |
| `dependencies` | Python version constraint and named package constraints |
| `inventory` | Artifact path, role, SHA-256 digest, and byte length |
| `conflicts` | Explicit contradictions or different active claims sharing a key |
| `review` | Null until approved; reviewer, timestamp, and content digest afterwards |

The manifest does not hash itself. Its canonical JSON representation, with review
set to null, is hashed for approval. Artifact hashes in that representation bind
the review to file contents. Approval metadata is not authenticated. ZIP CRC and
SHA-256 checks detect corruption but do not prove authorship or scientific validity.

## Knowledge records

Every record has `id`, `kind`, `status`, `content`, `tags`, `references`, `evidence`,
`artifacts`, `provenance`, `supersedes`, `contradicts`, and `sensitive`. Arrays may be
empty where appropriate. Optional `claim_key` groups competing assertions.

Kinds are context, decision, correction, failed_attempt, result, hypothesis,
question, procedure, and evidence. Statuses are verified, hypothesis, unresolved,
superseded, and unverified. IDs must be unique. Every selected record must point
to a packaged source descriptor. External source URIs are retained as references;
no network access occurs during inspection.

Verified records other than evidence records must reference verified evidence
records with packaged artifacts. A correction must identify superseded records,
which retain `superseded` status. Supersession cycles are invalid. These structural
checks do not judge whether an artifact actually supports a scientific assertion;
that requires review and scientific tests.

## Artifacts and dependencies

Artifact roles are procedure, test, evidence, instructions, data, or summary. Paths
are relative and restricted to portable ASCII components. Capsule content must
match the inventory exactly. The MVP does not support symlinks or binary files.
Tests are Python unittest files under `tests/`, normally named `test_*.py`.

Python constraints use PEP 440 specifiers. Packages use a distribution name with
version constraints, for example `numpy>=1.26,<3`. Direct URLs, extras, and markers
are deliberately excluded in this MVP. Declared packages are the union required
by selected artifacts, not all dependencies of the original memory store.
Verification compares installed distributions; it never installs them. Version
ranges express compatibility and are not a fully pinned reproducibility lock.

## Resource limits and version evolution

Limits: 200 files including the manifest, 20 MiB per artifact, 50 MiB total
artifacts, 50 MiB archive, and 2 MiB JSON metadata. Duplicate JSON keys and
nonfinite numbers are rejected. Schemas `1.0` and `1.1` are accepted explicitly, without permissive unknown fields.
Legacy 1.0 fixtures remain valid. The published alpha only reads 1.0 and therefore
rejects 1.1 rather than silently lose lineage; use the evolution development
implementation to receive evolved capsules. Creating from memory 1.0 still emits
1.0. Extending either supported parent emits 1.1. No implicit on-disk migration occurs.


## Format 1.1: lineage and external artifacts

Packaged `capsule-v1.1.schema.json` and `memory-v1.1.schema.json` add explicit
lineage and optional data references. Use `schema(version="1.1")` or
`schema("memory", version="1.1")` to obtain their JSON Schema definitions.

| Additional manifest field | Meaning |
| --- | --- |
| `capsule_id` | `sha256:` plus canonical content digest, excluding its own ID and setting review to null |
| `parent` | Null for a new root, or a direct-parent descriptor |
| `external_artifacts` | Descriptor array; records may reference their IDs via optional `external_artifacts` |

A parent descriptor requires `capsule_id`, `manifest_sha256`, `manifest_path`,
`summary_path`, `inherited_record_ids`, `new_record_ids`, and `revised_record_ids`.
The exact approved parent manifest and summary are inventoried under
`lineage/parent-<content-digest>/`. Its artifacts remain in the child's ordinary
inventory, without duplicating inherited files at the same path. Parent snapshots
accumulate for successive generations. Inspection checks their hashes, approvals,
record partitions, preserved provenance, dependencies, and artifact contents.
Only a superseded status may change on inherited knowledge, justified by a new
superseding record; changed text or procedures require new record IDs and paths.
Approval does not change the child's content ID, but its exact manifest checksum
includes approval metadata. Missing or modified embedded parents fail inspection;
the original capsule is optional. Content identities do not authenticate ancestry.

Every external descriptor requires `id`, `uri`, `sha256`, `size`, `description`,
`dependencies` (software/environment descriptions), and
`required_for_reproduction` (boolean). Supported URI schemes are HTTPS, file,
URN, and docker; embedded URI credentials are rejected. URI locations are
references only, not fetch instructions. `verify-external` checks an explicitly
provided local regular file against the declared bytes and hash, including binary
files. It never follows URLs or executes data. References cannot replace the
packaged evidence required for verified research records. Ordinary verification
reports unresolved external files as not checked, including required ones.

See the [C1 → C2 example](evolution.md) for schema usage, size measurements,
external audit artifacts, and independently verified lineage.
