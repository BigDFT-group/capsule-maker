# Poisson → periodic PSolver capsule

This is a fixed, experimentally validated research handover. The files are
downloadable below and accompany the current main implementation. They are not
included in the published
`v0.1.0-alpha` release, whose reader does not support C2's format 1.1.
Use the current evolution implementation with Python 3.11 or newer.

## Download and inspect

| Capsule | Research knowledge | Download size |
| --- | --- | ---: |
| [C1.zip](C1.zip) | 1D finite-difference solver, rejected sign, correction, evidence and second-order regressions | 6,175 bytes |
| [C2.zip](C2.zip) | All C1 knowledge plus 3D periodic PSolver procedures, normalization correction, results and validation criteria | 21,471 bytes |

Download [SHA256SUMS](SHA256SUMS) to check the exact archives. Hashes establish
integrity, not authorship or scientific truth. C2 contains its own parent metadata
and inherited files: **C1 is optional for receiving C2**. It is supplied here to
inspect the evolution and compare the two versions.

The [complete C2 knowledge summary](C2-summary.txt) is copied byte for byte from
C2's `SUMMARY.md`. Every capsule has this inspectable summary, structured records
in `manifest.json`, evidence, and receiving instructions. This page describes the
frozen demonstration; it does not modify the approved capsules or replace their
own provenance.

From a clone of the reviewed development checkout:

```bash
capsule-maker import docs/capsules/psolver-periodic-v1/C2.zip restored-C2
capsule-maker verify restored-C2
capsule-maker contents restored-C2 --path SUMMARY.md
capsule-maker resume restored-C2
```

These operations do not execute bundled code. Explicitly trusted regression
execution is a separate step. See [reuse prompts](../../reuse-psolver.md) to
run a fresh agent trial; keep this description and its answer-bearing summary
away from the receiving agent when measuring unaided retrieval.

See [how the harness uses this knowledge](../../psolver-knowledge.md) for exact
record excerpts, MCP tool arguments, and the transition to authorized execution.

## Knowledge carried by C2

C2 contains 15 curated scientific records, both investigations' provenance,
Python procedures, an original Fortran PSolver client, regression tests, numerical
results, versioned computational settings, and the parent manifest/summary.

The earlier study solves `-u''=pi² sin(pi*x)` on `[0,1]` with zero Dirichlet
boundaries. It preserves the wrong-sign attempt and corrected stencil, evidence
at 32/64/128 intervals, and the unresolved 256-interval continuation.

The new study uses a periodic cube `[0,2*pi)^3` in atomic units, with analytical
potential `sin(x)sin(y)sin(z)`. It records PSolver's Coulomb charge convention,
a rejected normalization and its correction, the potential gauge, in-place output
behavior, supported grid constraints, measured 16³–48³ results, and a remaining
64³ investigation. The precise assumptions and tolerances are in the capsule.

Hypotheses/unresolved claims remain distinguishable from verified evidence.
“Verified” is a curated status backed by files and numerical checks, not a
certification that all future uses or scientific interpretations are valid.

The capsule approval metadata records the known deterministic fixture review.
It is not an independent human peer review or a signature. The project owner
authorized publication under the documented single-maintainer policy; independent
scientific peer review remains outstanding.

## Validation and dependencies

The actual standalone PSolver 1.10 calculation used the pinned GNU/OpenMPI image
documented in the [evolution tutorial](../../evolution.md). A separate process
received C2 without the memory stores, reproduced the earlier 1D continuation,
and computed the new 64³ potential with maximum error `1.22e-15`.

Ordinary verification checks capsule integrity, lineage and declared Python
packages. Trusted bundled tests check the 1D solver plus recorded 3D evidence
and analytical charge construction. **They do not run compiled PSolver.** A real
3D continuation requires explicit code trust and a separately installed compiled
environment. Neither PSolver binaries nor the Docker image are redistributed in
these archives. The original client and capsule artifacts are MIT licensed;
external scientific software retains its own licenses.

C2 expands to 54,848 bytes. Its optional raw audit archive is about 1.21 MB and
is deliberately not included in this gallery. C2 references it by checksum and
size; it is not required to retrieve knowledge or regenerate the calculation.
Regenerating the demo creates a new audit archive and capsule with their own
checksums. Preserve a particular trial's raw archive separately if auditing its
exact arrays/logs is necessary. This lightweight capsule does not constitute a
fully archived executable environment.

## Contributor maintenance

Treat this folder as a versioned fixture. Do not replace the ZIPs in place or edit
an extracted capsule's manifest. A changed investigation belongs in a new folder
and, where appropriate, a new child capsule. Document scope, provenance, license,
archive hashes/sizes, software requirements, scientific checks, and limitations.
Import and verify contributed archives before review, and execute their code only
with explicit trust in an appropriate environment. Keep credentials, original
private conversations, compiled environments, and unnecessary large arrays out
of the gallery. Use the project's normal contributor and scientific review process.
