# Memory adapter contract and future integrations

## Implemented reference: local JSON files

`MemoryAdapter` is an abstract Python interface with two methods:

```python
from capsule_maker import MemoryAdapter

class MyAdapter(MemoryAdapter):
    def snapshot(self) -> dict:
        # Return normalized records, source descriptors, and artifact metadata.
        ...

    def read_artifact(self, path: str) -> bytes:
        # Return a declared UTF-8 file without executing it.
        ...
```

This illustrates the contract; it is not a working backend adapter. The real
`LocalFileAdapter(memory_file)` reads JSON and declared artifacts relative to the
memory file. It rejects unsafe paths and symlinks. A custom adapter can return
records from any backend while keeping the capsule independent of that service.

The normalized snapshot follows `memory-v1.schema.json`: `format_version`,
`origin`, `records`, `sources`, `python`, and `artifacts`. Each artifact declares
`path`, `role`, and `packages`. Scientific records use the same shape as capsule
records. The core selects a goal closure, checks required source and artifact
availability, and takes the union of selected artifact dependencies.

Adapters should supply a consistent read-only snapshot. They do not create
capsule approvals, claim human review, execute procedures, or re-consolidate
upstream knowledge. Do not label unsupported assertions as verified merely to
pass structural checks.

## AOM design: not yet implemented

The supplied *Capsule-Maker and AOM* document describes episode capture, recipe
consolidation, verdicts, corrections, pending skills, and frozen memories. These
remain AOM responsibilities. Capsule-Maker should map already-curated information
into neutral records and package selected artifacts and provenance.

Before writing an adapter, verify the real upstream API or supported export format
and version. Establish how to obtain stable episode/recipe IDs, goal or intention
metadata, verdicts, correction relationships, evidence, source references, and
reusable procedures. Confirm access permissions, consistency semantics, and
redistribution rights. Add fixtures based on an actual sanitized supported export
and test the same neutral handover contract.

No AOM endpoint, method, database layout, or authentication flow is assumed here.
There is deliberately no fake adapter advertised as an integration.

## Other planned sources and capabilities

Graphiti, Mem0, Cognee, and Hindsight could implement the same normalized adapter
contract after verifying their real interfaces. Their capture and consolidation
mechanisms do not belong in Capsule-Maker's core.

Paper2Agent-derived scientific functions may later become procedure artifacts
with dependencies, evidence, licensing, and regression tests. BigDFT/PyBigDFT
workflows and independent LLM environments are future scientific demonstrations.
Neither integration is implemented or required for the local Poisson cycle.
