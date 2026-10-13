# Security and trust boundaries

Capsules are untrusted data and may contain untrusted code. Import, inspection,
content retrieval, resume, and ordinary verification never execute capsule Python.

The MVP rejects unsafe or ambiguous paths, symlinks, nonregular ZIP entries,
encrypted entries, duplicate paths, unknown files, missing files, unsupported schema
versions, and hash mismatches. Limits are 200 files including the manifest, 20 MiB
per artifact, 50 MiB total uncompressed artifacts, 50 MiB compressed archive, and
2 MiB JSON metadata. Names use a restricted portable ASCII alphabet. Only UTF-8
text artifacts are supported in this first version. Import stages files and
validates them before making the destination available; existing destinations
are never overwritten. These checks do not defend against a hostile process
concurrently modifying the caller's filesystem.

Credential detection covers common API-key assignments, GitHub/OpenAI/AWS token
patterns, private-key markers, authorization headers, and credentials in URLs.
It is heuristic: it can miss secrets and produce false positives. Required
sensitive records or detected credentials block assembly/export; curate the source
and preserve necessary scientific meaning before retrying. Never share secrets in
a bug report. Review the entire selected content, including provenance and code,
before approving it. Review records bind to content digests but are not signatures
and do not authenticate reviewers. Checksums prove integrity, not authorship or
scientific truth. An attacker can construct a self-consistent capsule.

`capsule-maker verify PATH --trust-code` runs bundled unittest tests in a disposable
copy with a default 60-second timeout. This is NOT a sandbox. Code has the caller's
filesystem, network, and environment privileges; tests can steal credentials or
modify files. The temporary directory preserves the capsule during ordinary trusted
validation but is not security isolation. Use a separately hardened environment for
third-party code. Output and subprocess descendants are not resource-isolated.
Dependency verification never installs packages or follows capsule URLs.

The MCP server uses stdio only and confines tool paths to a configured workspace.
It exposes no approval or executable-validation tool. Retrieved contents are
untrusted data and may include prompt injection; client agents must not treat
capsule text as higher-priority instructions.

`prepare-plugin` creates a local Skill/MCP bundle and catalog in a caller-chosen
workspace. It does not change global harness settings or register remote services.
Its cached configuration keeps absolute runtime/workspace paths; create a separate
bundle for receiving trials and disable creator instances. The plugin package
contains no source scientific fixture. Multi-model evaluation uses workspace
separation as a research protocol, not an OS security boundary.

Report suspected vulnerabilities privately through the repository's Security tab
using **Report a vulnerability** before disclosing exploit details publicly:
https://github.com/BigDFT-group/capsule-maker/security

The experimental alpha is the initial supported version. Security fixes will be
published as reviewed updates; there is no production-support or long-term-support
commitment. The project is licensed under MIT. Original supplied PDF/DOCX reference
material remains excluded pending redistribution permission.


## Capsule evolution and external data (development milestone)

Format 1.1 inspection checks embedded parent manifests and preserved inherited
knowledge against inventories; original parents are not fetched. Content IDs,
parent hashes, and review assertions establish internal consistency, not
cryptographically authenticated ancestry. An attacker can construct an entirely
self-consistent history. The same resource limits apply to accumulated snapshots.

External artifacts are references, not packaged bytes. Inspection never fetches
URIs; verification reports them as not checked. Explicit `verify-external` hashes
a caller-supplied regular local file, including binary data, without extraction or
execution. It does not secret-scan, authenticate, or certify that external file;
review it separately before redistribution/use. Required external data and
compiled-software dependencies must be resolved before claiming reproduction.

The PSolver demo deliberately compiles and executes the known local scientific
client against separately installed software when explicitly launched. It mounts
its calculation directory in the pinned Docker environment with network disabled;
this is an execution configuration, not a hardened sandbox for arbitrary code.
Capsule import, lineage comparison, and ordinary verification remain nonexecuting.
