"""Immutable research accumulation with explicit lineage and optional external data."""

from __future__ import annotations

import copy
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit

from packaging.specifiers import SpecifierSet

from .adapters import MemoryAdapter
from .core import (
    MAX_MANIFEST_BYTES,
    CapsuleError,
    Goal,
    _assemble_capsule,
    _index,
    _references,
    _requirements,
    canonical,
    conflicts,
    inspect_capsule,
    read_bytes,
    read_json,
    review_digest,
    safe_path,
    scan_secrets,
    select,
    validate_schema,
)


def capsule_identifier(manifest: dict) -> str:
    """Content identity for both legacy 1.0 and new 1.1 capsules; not authentication."""
    return "sha256:" + review_digest(manifest)


def _merge_unique(inherited: list[dict], additions: list[dict], key: str) -> list[dict]:
    merged = copy.deepcopy(_index(inherited, key))
    for item in additions:
        identifier = item[key]
        if identifier in merged and canonical(merged[identifier]) != canonical(item):
            raise CapsuleError(f"Conflicting inherited {key}; use a new identifier")
        merged[identifier] = copy.deepcopy(item)
    return [merged[i] for i in sorted(merged)]


def _validate_external(descriptors: list[dict]) -> set[str]:
    by_id = _index(descriptors, "id")
    for item in descriptors:
        try:
            uri = urlsplit(item["uri"])
        except ValueError as exc:
            raise CapsuleError("Invalid external artifact URI") from exc
        if uri.scheme not in {"https", "file", "urn", "docker"} or uri.username or uri.password:
            raise CapsuleError(
                "External artifact URI must use https, file, urn, or docker without credentials"
            )
        if uri.scheme == "https" and not uri.netloc:
            raise CapsuleError("External HTTPS artifact URI requires a host")
    return set(by_id)


def extend_capsule(
    parent_directory: str | Path, adapter: MemoryAdapter, goal: Goal, destination: str | Path
) -> dict:
    """Keep all parent knowledge, select additions, and write a new unapproved child.

    New records must have new IDs. A new correction can supersede an inherited
    record: only its status becomes superseded in the child, with the original
    record preserved exactly in the checksummed parent snapshot. Artifact paths
    are immutable; identical reused paths share one inventory entry. No hardlinks
    or external fetches are used.
    """
    parent_root = Path(parent_directory)
    parent = inspect_capsule(parent_root)
    if not parent["review"]:
        raise CapsuleError("Parent capsule must be reviewed before extension")
    delta = adapter.snapshot()
    validate_schema(delta, "memory")
    _requirements({"python": delta["python"], "packages": []})
    old_ids = {r["id"] for r in parent["records"]}
    if old_ids.intersection(r["id"] for r in delta["records"]):
        raise CapsuleError("New knowledge must use new record IDs")
    inherited_external = parent.get("external_artifacts", [])
    external = _merge_unique(inherited_external, delta.get("external_artifacts", []), "id")
    _validate_external(external)
    sources = _merge_unique(parent["sources"], delta["sources"], "id")
    merged_records = copy.deepcopy(parent["records"] + delta["records"])
    # Selection can reference inherited records, while all parent records survive regardless of tags.
    combined = {
        "format_version": "1.1",
        "origin": delta["origin"],
        "records": merged_records,
        "sources": sources,
        "python": delta["python"],
        "artifacts": delta["artifacts"],
        "external_artifacts": external,
    }
    selected = select(combined, goal)
    additions = [r for r in selected if r["id"] not in old_ids]
    if not additions:
        raise CapsuleError("Evolution goal selected no new knowledge")
    records = copy.deepcopy(parent["records"] + additions)
    by_id = _index(records, "id")
    revised = set()
    for rec in additions:
        for older in rec["supersedes"]:
            if older in old_ids and by_id[older]["status"] != "superseded":
                by_id[older]["status"] = "superseded"
                revised.add(older)
    records = [by_id[i] for i in sorted(by_id)]
    needed_sources = {i for r in records for i in r["provenance"]}
    sources = [item for item in sources if item["id"] in needed_sources]
    needed_external = {e["id"] for e in inherited_external} | {
        i for rec in additions for i in rec.get("external_artifacts", [])
    }
    external = [item for item in external if item["id"] in needed_external]
    external_ids = _validate_external(external)
    needed_paths = {name for r in additions for name in r["artifacts"]}
    descriptors = _index(delta["artifacts"], "path")
    inherited_inventory = _index(parent["inventory"], "path")
    if not needed_paths <= (descriptors.keys() | inherited_inventory.keys()):
        raise CapsuleError("Missing artifact needed by the new investigation")
    contents = {
        name: (read_bytes(safe_path(parent_root, name)), item["role"])
        for name, item in inherited_inventory.items()
        if name != "SUMMARY.md"
    }
    for name in sorted(needed_paths):
        if name in {"manifest.json", "SUMMARY.md"} or name.startswith("lineage/"):
            raise CapsuleError("New scientific artifact uses a reserved lineage or metadata path")
        if name in descriptors:
            data = adapter.read_artifact(name)
            role = descriptors[name]["role"]
            if name in contents and contents[name] != (data, role):
                raise CapsuleError(
                    "Inherited artifacts are immutable; use a new path for a revised procedure"
                )
            contents[name] = (data, role)
    parent_id = capsule_identifier(parent)
    prefix = f"lineage/parent-{parent_id.split(':')[1]}"
    manifest_path, summary_path = f"{prefix}/manifest.json", f"{prefix}/SUMMARY.md"
    parent_bytes = read_bytes(safe_path(parent_root, "manifest.json"), MAX_MANIFEST_BYTES)
    contents[manifest_path] = (parent_bytes, "data")
    contents[summary_path] = (read_bytes(safe_path(parent_root, "SUMMARY.md")), "summary")
    packages = set(parent["dependencies"]["packages"])
    packages.update(
        p for name in needed_paths if name in descriptors for p in descriptors[name]["packages"]
    )
    python = str(SpecifierSet(parent["dependencies"]["python"] + "," + delta["python"]))
    manifest = {
        "schema_version": "1.1",
        "capsule_id": "sha256:" + "0" * 64,
        "origin": delta["origin"],
        "goal": goal.as_dict(),
        "records": records,
        "sources": sources,
        "dependencies": {"python": python, "packages": sorted(packages)},
        "inventory": [],
        "conflicts": conflicts(records),
        "review": None,
        "external_artifacts": external,
        "parent": {
            "capsule_id": parent_id,
            "manifest_sha256": sha256(parent_bytes).hexdigest(),
            "manifest_path": manifest_path,
            "summary_path": summary_path,
            "inherited_record_ids": sorted(old_ids),
            "new_record_ids": sorted(r["id"] for r in additions),
            "revised_record_ids": sorted(revised),
        },
    }
    _references(records, sources, set(contents), external_ids)
    scan_secrets(canonical(manifest), "evolution metadata")
    return _assemble_capsule(manifest, contents, destination)


def validate_lineage(root: Path, manifest: dict) -> None:
    """Validate embedded parent evidence and inheritance without the original parent."""
    _validate_external(manifest["external_artifacts"])
    if manifest["capsule_id"] != capsule_identifier(manifest):
        raise CapsuleError("Capsule identifier does not match content")
    root_inventory = _index(manifest["inventory"], "path")
    current = manifest
    visited = set()
    while current.get("parent"):
        lineage = current["parent"]
        if lineage["capsule_id"] in visited:
            raise CapsuleError("Repeated parent lineage")
        visited.add(lineage["capsule_id"])
        if (
            lineage["manifest_path"] not in root_inventory
            or lineage["summary_path"] not in root_inventory
        ):
            raise CapsuleError("Missing packaged parent information")
        parent_bytes = read_bytes(safe_path(root, lineage["manifest_path"]), MAX_MANIFEST_BYTES)
        if sha256(parent_bytes).hexdigest() != lineage["manifest_sha256"]:
            raise CapsuleError("Parent manifest checksum mismatch")
        parent = read_json(safe_path(root, lineage["manifest_path"]))
        validate_schema(parent)
        _requirements(parent["dependencies"])
        _validate_external(parent.get("external_artifacts", []))
        if capsule_identifier(parent) != lineage["capsule_id"]:
            raise CapsuleError("Parent capsule identifier mismatch")
        if not parent["review"] or parent["review"]["digest"] != review_digest(parent):
            raise CapsuleError("Parent approval is missing or stale")
        if parent.get("capsule_id") and parent["capsule_id"] != capsule_identifier(parent):
            raise CapsuleError("Embedded parent identity mismatch")
        _references(
            parent["records"],
            parent["sources"],
            {i["path"] for i in parent["inventory"]},
            {e["id"] for e in parent.get("external_artifacts", [])},
        )
        if parent["conflicts"] != conflicts(parent["records"]):
            raise CapsuleError("Embedded parent conflict report mismatch")
        before = _index(parent["records"], "id")
        after = _index(current["records"], "id")
        if not before.keys() <= after.keys() or sorted(before) != lineage["inherited_record_ids"]:
            raise CapsuleError("Inherited research knowledge is missing")
        new_ids = after.keys() - before.keys()
        if sorted(new_ids) != lineage["new_record_ids"]:
            raise CapsuleError("New knowledge provenance does not match records")
        revised = []
        for record_id, original in before.items():
            revised_record = after[record_id]
            if revised_record != original:
                expected = {**original, "status": "superseded"}
                if revised_record != expected or not any(
                    record_id in after[i]["supersedes"] for i in new_ids
                ):
                    raise CapsuleError(
                        "Inherited record changed without a valid superseding decision"
                    )
                revised.append(record_id)
        if sorted(revised) != lineage["revised_record_ids"]:
            raise CapsuleError("Revised decision provenance mismatch")
        after_sources = _index(current["sources"], "id")
        for source in parent["sources"]:
            if after_sources.get(source["id"]) != source:
                raise CapsuleError("Inherited source provenance changed")
        after_external = _index(current["external_artifacts"], "id")
        for descriptor in parent.get("external_artifacts", []):
            if after_external.get(descriptor["id"]) != descriptor:
                raise CapsuleError("Inherited external artifact changed")
        if not set(parent["dependencies"]["packages"]) <= set(current["dependencies"]["packages"]):
            raise CapsuleError("Inherited package requirements removed")
        if not set(SpecifierSet(parent["dependencies"]["python"])) <= set(
            SpecifierSet(current["dependencies"]["python"])
        ):
            raise CapsuleError("Inherited Python requirements removed")
        for entry in parent["inventory"]:
            target = lineage["summary_path"] if entry["path"] == "SUMMARY.md" else entry["path"]
            carried = root_inventory.get(target)
            if not carried or any(carried[k] != entry[k] for k in ("sha256", "size", "role")):
                raise CapsuleError("Inherited artifact missing or modified")
        current = parent


def verify_parent(child_directory: str | Path, parent_directory: str | Path) -> dict:
    child = inspect_capsule(child_directory)
    if not child.get("parent"):
        raise CapsuleError("Capsule has no recorded parent")
    parent = inspect_capsule(parent_directory)
    data = read_bytes(safe_path(Path(parent_directory), "manifest.json"), MAX_MANIFEST_BYTES)
    expected = child["parent"]
    if (
        capsule_identifier(parent) != expected["capsule_id"]
        or sha256(data).hexdigest() != expected["manifest_sha256"]
    ):
        raise CapsuleError("Provided parent does not match the recorded parent")
    return {"parent": expected["capsule_id"], "matches": True}


def compare_capsules(before_directory: str | Path, after_directory: str | Path) -> dict:
    before, after = inspect_capsule(before_directory), inspect_capsule(after_directory)

    def difference(left, right, key):
        left, right = _index(left, key), _index(right, key)
        shared = left.keys() & right.keys()
        return {
            "added": sorted(right.keys() - left.keys()),
            "removed": sorted(left.keys() - right.keys()),
            "changed": sorted(i for i in shared if left[i] != right[i]),
            "unchanged": sorted(i for i in shared if left[i] == right[i]),
        }

    relationship = bool(
        after.get("parent") and after["parent"]["capsule_id"] == capsule_identifier(before)
    )
    if relationship:
        verify_parent(after_directory, before_directory)
    return {
        "before_id": capsule_identifier(before),
        "after_id": capsule_identifier(after),
        "direct_child": relationship,
        "records": difference(before["records"], after["records"], "id"),
        "artifacts": difference(before["inventory"], after["inventory"], "path"),
        "external_artifacts": difference(
            before.get("external_artifacts", []), after.get("external_artifacts", []), "id"
        ),
        "before_size": capsule_size(before_directory),
        "after_size": capsule_size(after_directory),
    }


def capsule_size(directory: str | Path) -> dict:
    manifest = inspect_capsule(directory)
    inventory = manifest["inventory"]
    metadata_bytes = len(
        read_bytes(safe_path(Path(directory), "manifest.json"), MAX_MANIFEST_BYTES)
    )
    return {
        "files": len(inventory) + 1,
        "manifest_bytes": metadata_bytes,
        "artifact_bytes": sum(i["size"] for i in inventory),
        "directory_bytes": metadata_bytes + sum(i["size"] for i in inventory),
        "unique_artifact_bytes": sum(
            i["size"] for i in {e["sha256"]: e for e in inventory}.values()
        ),
        "external_declared_bytes": sum(e["size"] for e in manifest.get("external_artifacts", [])),
    }


def verify_external_artifact(
    directory: str | Path, artifact_id: str, local_file: str | Path
) -> dict:
    """Hash an explicitly supplied local file. Never fetch a URI or execute content."""
    manifest = inspect_capsule(directory)
    descriptors = _index(manifest.get("external_artifacts", []), "id")
    if artifact_id not in descriptors:
        raise CapsuleError("Unknown external artifact")
    path = Path(local_file)
    if path.is_symlink() or not path.is_file():
        raise CapsuleError("External artifact file is missing or unsafe")
    expected = descriptors[artifact_id]
    if path.stat().st_size != expected["size"]:
        raise CapsuleError("External artifact size mismatch")
    digest = sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            if size > expected["size"]:
                raise CapsuleError("External artifact changed while checking")
            digest.update(chunk)
    if size != expected["size"] or digest.hexdigest() != expected["sha256"]:
        raise CapsuleError("External artifact integrity failure")
    return {"id": artifact_id, "integrity": True, "size": size, "sha256": digest.hexdigest()}
