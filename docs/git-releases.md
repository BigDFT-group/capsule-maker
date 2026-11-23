# Git-backed capsule releases

A dedicated Git repository holds the approved capsule files at its root.
Each reviewed revision can be shared as one ZIP. The existing capsule schemas
and standalone ZIPs remain supported.

| File | Purpose |
| --- | --- |
| `README.md` | Versioned receiving instructions |
| `release.json` | Envelope version, capsule ID, full Git commit, branch ref and SHA-256 digests of the other three files |
| `capsule.bundle` | The selected local branch and its reachable Git history |
| `capsule.zip` | The approved Capsule-Maker snapshot at that commit |

For schema 1.0, the release uses the SHA-256 content digest as the capsule ID.
Digests detect mismatches and do not authenticate the publisher. The release
creator checks the archived commit and bundle ref. A Git-free import checks
the payload hashes and the snapshot identity without interpreting Git history.

## Receive without Git

```sh
capsule-maker import-release C2-release.zip restored
capsule-maker verify restored --integrity-only
capsule-maker resume restored
```

An older Capsule-Maker installation can open the inner `capsule.zip` with its
ordinary `import` command if it supports the inner schema. MCP clients can
inspect the restored directory with their existing capsule tools.

## Receive and inspect the history

Extract `capsule.bundle` from the reviewed release, then use:

```sh
git bundle list-heads capsule.bundle
git clone --branch main capsule.bundle C2-history
git -C C2-history rev-parse HEAD
git -C C2-history log --oneline
```

Use the branch named by `git_ref` in `release.json` after removing the
`refs/heads/` prefix. Compare the reported commit with `git_commit`.
Use the separate imported directory for Capsule-Maker operations, since a Git
checkout also contains `.git`. Keep the Git checkout for collaboration.

## Update and release

Start a branch with `git switch -c investigation`. Import the approved parent
into a separate directory, use `capsule-maker extend` to build a new snapshot,
verify it, and approve the reviewed content. Stage only the new approved
snapshot in the dedicated Git repository. Review the staged diff and commit it.

```sh
capsule-maker release C2-history --ref investigation --output C3-release.zip
```

The command reads a committed local branch, independent of pending working tree
edits. It expects a complete local Git repository. Review all reachable commits
before bundling, including deleted material and commit metadata. Keep private or
unlicensed material out of Git and store large research artifacts externally
with checksums. Capsule-Maker scans and validates the approved snapshot. The
bundle's historical content needs a separate review.

A harness with Git tooling can use it directly. A harness with a terminal can
run Git commands through that terminal. If neither is available, the agent can
read and propose changes for a contributor to commit.
