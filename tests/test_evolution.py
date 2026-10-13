"""Independent lineage, inheritance, trust, and external-blob failure tests."""

import json
import shutil
import subprocess
import sys
from hashlib import sha256

import pytest
from jsonschema import Draft202012Validator

from capsule_maker import (
    CapsuleError,
    Goal,
    LocalFileAdapter,
    approve_capsule,
    capsule_identifier,
    capsule_size,
    compare_capsules,
    create_capsule,
    export_capsule,
    extend_capsule,
    import_capsule,
    inspect_capsule,
    resume_knowledge,
    verify_capsule,
    verify_external_artifact,
    verify_parent,
)
from capsule_maker.core import review_digest, schema


def delta(tmp_path, *, supersedes=(), external=False):
    directory = tmp_path / "new-memory"
    directory.mkdir()
    record = {
        "id": "new-observation",
        "kind": "decision",
        "status": "verified",
        "content": "New investigation preserves the earlier solver and correction.",
        "tags": ["evolution"],
        "references": ["correct-sign"],
        "evidence": ["new-evidence"],
        "artifacts": ["new.txt", "solver.py"],
        "provenance": ["session-b"],
        "supersedes": list(supersedes),
        "contradicts": [],
        "sensitive": False,
    }
    evidence = {
        **record,
        "id": "new-evidence",
        "kind": "evidence",
        "references": [],
        "artifacts": ["new.txt"],
        "evidence": [],
        "supersedes": [],
    }
    (directory / "new.txt").write_text("A new computed scientific observation.\n")
    memory = {
        "format_version": "1.1",
        "origin": {"backend": "local-file", "description": "Session B"},
        "records": [record, evidence],
        "sources": [
            {"id": "session-b", "uri": "urn:session-b", "description": "New investigation"}
        ],
        "python": ">=3.11,<4",
        "artifacts": [{"path": "new.txt", "role": "evidence", "packages": []}],
        "external_artifacts": [],
    }
    if external:
        blob = tmp_path / "large.bin"
        blob.write_bytes(bytes(range(256)) * 8192)
        memory["external_artifacts"] = [
            {
                "id": "raw",
                "uri": "urn:sha256:" + sha256(blob.read_bytes()).hexdigest(),
                "sha256": sha256(blob.read_bytes()).hexdigest(),
                "size": blob.stat().st_size,
                "description": "Optional binary data",
                "dependencies": ["PSolver==1.10"],
                "required_for_reproduction": False,
            }
        ]
        evidence["external_artifacts"] = ["raw"]
    path = directory / "memory.json"
    path.write_text(json.dumps(memory))
    return path


def change(memory, fn):
    value = json.loads(memory.read_text())
    fn(value)
    memory.write_text(json.dumps(value))


def reseal(root, fn):
    """Model a self-consistent attacker; lineage must reject semantic tampering too."""
    path = root / "manifest.json"
    value = json.loads(path.read_text())
    fn(value)
    value["review"] = None
    value["capsule_id"] = "sha256:" + review_digest(value)
    path.write_text(json.dumps(value))


@pytest.fixture
def parent(capsule):
    approve_capsule(capsule, "fixture-review")
    return capsule


def test_inheritance_approval_identity_and_roundtrip(parent, tmp_path):
    original = {
        p.relative_to(parent).as_posix(): p.read_bytes() for p in parent.rglob("*") if p.is_file()
    }
    child = tmp_path / "child"
    manifest = extend_capsule(
        parent, LocalFileAdapter(delta(tmp_path)), Goal("Extend", ("evolution",)), child
    )
    Draft202012Validator(schema(version="1.1")).validate(manifest)
    assert manifest["parent"]["capsule_id"] == capsule_identifier(inspect_capsule(parent))
    assert manifest["parent"]["manifest_sha256"] == sha256(original["manifest.json"]).hexdigest()
    assert manifest["review"] is None
    assert "Supersedes: wrong-sign" in (child / "SUMMARY.md").read_text()
    assert {
        p.relative_to(parent).as_posix(): p.read_bytes() for p in parent.rglob("*") if p.is_file()
    } == original
    comparison = compare_capsules(parent, child)
    assert comparison["direct_child"] and comparison["records"]["added"] == [
        "new-evidence",
        "new-observation",
    ]
    assert comparison["records"]["removed"] == comparison["records"]["changed"] == []
    assert sum(i["path"] == "solver.py" for i in manifest["inventory"]) == 1
    with pytest.raises(CapsuleError, match="approval"):
        export_capsule(child, tmp_path / "blocked.zip")
    approve_capsule(child, "child-review")
    export_capsule(child, tmp_path / "child.zip")
    shutil.rmtree(parent)
    shutil.rmtree(tmp_path / "new-memory")
    restored = tmp_path / "restored"
    assert import_capsule(tmp_path / "child.zip", restored) == inspect_capsule(child)
    assert verify_capsule(restored)["lineage"] == "verified"
    assert {"correct-sign", "wrong-sign", "new-observation"} <= {
        r["id"] for r in resume_knowledge(restored)["records"]
    }
    assert verify_capsule(restored, trust_code=True)["tests"] == "passed"
    run = subprocess.run(
        [sys.executable, "-I", "-m", "capsule_maker.cli", "resume", str(restored)],
        cwd=tmp_path,
        capture_output=True,
        check=False,
        text=True,
    )
    assert run.returncode == 0 and "new-observation" in run.stdout and "correct-sign" in run.stdout


def test_revision_preserves_original_decision(parent, tmp_path):
    child = tmp_path / "child"
    original = inspect_capsule(parent)
    manifest = extend_capsule(
        parent,
        LocalFileAdapter(delta(tmp_path, supersedes=["boundary-decision"])),
        Goal("Evolve", ("evolution",)),
        child,
    )
    assert manifest["parent"]["revised_record_ids"] == ["boundary-decision"]
    assert (
        next(r for r in manifest["records"] if r["id"] == "boundary-decision")["status"]
        == "superseded"
    )
    assert inspect_capsule(parent) == original
    assert compare_capsules(parent, child)["records"]["changed"] == ["boundary-decision"]


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda v: v["parent"].update(manifest_sha256="0" * 64), "checksum"),
        (lambda v: v["parent"].update(capsule_id="sha256:" + "0" * 64), "identifier"),
        (lambda v: v["parent"].update(manifest_path="missing.json"), "Missing packaged parent"),
        (lambda v: v["parent"]["inherited_record_ids"].clear(), "Inherited research"),
        (lambda v: v["parent"]["new_record_ids"].clear(), "New knowledge"),
        (
            lambda v: v["records"][0].update(content="Rewritten inherited science"),
            "Inherited record",
        ),
        (lambda v: v["dependencies"]["packages"].clear(), "requirements removed"),
    ],
)
def test_semantic_lineage_tampering(parent, tmp_path, mutation, message):
    child = tmp_path / "child"
    extend_capsule(parent, LocalFileAdapter(delta(tmp_path)), Goal("Evolve", ("evolution",)), child)
    reseal(child, mutation)
    with pytest.raises(CapsuleError, match=message):
        inspect_capsule(child)


def test_corrupt_parent_and_wrong_actual_parent(parent, memory, tmp_path):
    child = tmp_path / "child"
    manifest = extend_capsule(
        parent, LocalFileAdapter(delta(tmp_path)), Goal("Evolve", ("evolution",)), child
    )
    assert verify_parent(child, parent)["matches"]
    other = tmp_path / "other"
    create_capsule(LocalFileAdapter(memory), Goal("Literature", ("literature",)), other)
    approve_capsule(other, "review")
    with pytest.raises(CapsuleError, match="does not match"):
        verify_parent(child, other)
    (child / manifest["parent"]["manifest_path"]).write_text("{}")
    with pytest.raises(CapsuleError, match="Integrity failure"):
        inspect_capsule(child)


def test_external_binary_size_hash_and_no_fetch(parent, tmp_path):
    child = tmp_path / "child"
    extend_capsule(
        parent,
        LocalFileAdapter(delta(tmp_path, external=True)),
        Goal("Evolve", ("evolution",)),
        child,
    )
    blob = tmp_path / "large.bin"
    assert capsule_size(child)["external_declared_bytes"] == blob.stat().st_size
    assert capsule_size(child)["directory_bytes"] < blob.stat().st_size / 20
    assert verify_capsule(child)["external_artifacts"][0]["status"] == "not checked"
    assert verify_external_artifact(child, "raw", blob)["integrity"]
    data = bytearray(blob.read_bytes())
    data[0] ^= 1
    blob.write_bytes(data)
    with pytest.raises(CapsuleError, match="integrity"):
        verify_external_artifact(child, "raw", blob)
    blob.write_bytes(b"truncated")
    with pytest.raises(CapsuleError, match="size mismatch"):
        verify_external_artifact(child, "raw", blob)
    blob.unlink()
    assert verify_capsule(child)["integrity"]  # optional external blob isn't standalone knowledge
    with pytest.raises(CapsuleError, match="missing or unsafe"):
        verify_external_artifact(child, "raw", blob)


def test_three_generations(parent, tmp_path):
    memory = delta(tmp_path)
    second = tmp_path / "second"
    extend_capsule(parent, LocalFileAdapter(memory), Goal("Evolve", ("evolution",)), second)
    approve_capsule(second, "second-review")
    value = json.loads(memory.read_text())
    for r in value["records"]:
        r["id"] = "third-" + r["id"]
        r["evidence"] = ["third-new-evidence"] if r["kind"] != "evidence" else []
    memory.write_text(json.dumps(value))
    third = tmp_path / "third"
    extend_capsule(second, LocalFileAdapter(memory), Goal("Evolve", ("evolution",)), third)
    approve_capsule(third, "third-review")
    export_capsule(third, tmp_path / "third.zip")
    shutil.rmtree(parent)
    shutil.rmtree(second)
    assert import_capsule(tmp_path / "third.zip", tmp_path / "restored")["parent"]
    assert verify_capsule(tmp_path / "restored")["lineage"] == "verified"


@pytest.mark.parametrize(
    "failure", ["duplicate", "modified", "missing", "empty", "sensitive", "secret", "external"]
)
def test_extension_fails_closed(parent, tmp_path, failure):
    memory = delta(tmp_path)
    if failure == "duplicate":
        change(memory, lambda v: v["records"][0].update(id="correct-sign"))
    elif failure == "modified":
        (memory.parent / "solver.py").write_text("changed solver")
        change(
            memory,
            lambda v: v["artifacts"].append(
                {"path": "solver.py", "role": "procedure", "packages": []}
            ),
        )
    elif failure == "missing":
        (memory.parent / "new.txt").unlink()
    elif failure == "empty":
        change(memory, lambda v: [r.update(tags=[]) for r in v["records"]])
    elif failure == "sensitive":
        change(memory, lambda v: v["records"][0].update(sensitive=True))
    elif failure == "secret":
        (memory.parent / "new.txt").write_text('password="never-export-this-value"')
    else:
        change(memory, lambda v: v["records"][0].update(external_artifacts=["missing"]))
    with pytest.raises(CapsuleError):
        extend_capsule(
            parent, LocalFileAdapter(memory), Goal("Evolve", ("evolution",)), tmp_path / "broken"
        )
    assert not (tmp_path / "broken").exists()
    assert inspect_capsule(parent)["review"]


def test_unapproved_parent_rejected(capsule, tmp_path):
    with pytest.raises(CapsuleError, match="reviewed"):
        extend_capsule(
            capsule,
            LocalFileAdapter(delta(tmp_path)),
            Goal("Evolve", ("evolution",)),
            tmp_path / "child",
        )


def test_cli_extension_and_comparison(parent, tmp_path):
    memory = delta(tmp_path)
    child = tmp_path / "child"

    def call(*args):
        run = subprocess.run(
            [sys.executable, "-I", "-m", "capsule_maker.cli", *map(str, args)],
            capture_output=True,
            check=False,
            text=True,
        )
        assert run.returncode == 0, run.stderr
        return json.loads(run.stdout)

    assert call("extend", parent, memory, child, "--goal", "Evolve", "--tag", "evolution")["parent"]
    assert call("compare", parent, child)["direct_child"]
    assert call("verify-parent", child, parent)["matches"]
    assert call("size", child)["files"] > 1


def test_standalone_11_identity_and_external_reference(memory, tmp_path):
    value = json.loads(memory.read_text())
    value.update(format_version="1.1", external_artifacts=[])
    memory.write_text(json.dumps(value))
    root = tmp_path / "root11"
    created = create_capsule(LocalFileAdapter(memory), Goal("Poisson", ("convergence",)), root)
    assert created["schema_version"] == "1.1" and created["parent"] is None
    identity = created["capsule_id"]
    approved = approve_capsule(root, "review")
    assert approved["capsule_id"] == identity == capsule_identifier(approved)
    assert verify_capsule(root)["lineage"] == "no parent"
    export_capsule(root, tmp_path / "root11.zip")
    assert import_capsule(tmp_path / "root11.zip", tmp_path / "restored11") == approved


def test_new_incompatible_requirements_are_retained(parent, tmp_path):
    memory = delta(tmp_path)
    change(memory, lambda v: v["artifacts"][0].update(packages=["numpy<0.1"]))
    child = tmp_path / "child"
    extended = extend_capsule(
        parent, LocalFileAdapter(memory), Goal("Evolve", ("evolution",)), child
    )
    assert set(extended["dependencies"]["packages"]) == {"numpy<0.1", "numpy>=1.26,<3"}
    with pytest.raises(CapsuleError, match="Incompatible environment"):
        verify_capsule(child)
    assert verify_capsule(child, environment=False)["integrity"]


@pytest.mark.parametrize(
    "uri", ["http://example.org/data", "https:///missing-host", "https://[invalid"]
)
def test_external_uri_rejected_without_fetch(parent, tmp_path, uri):
    memory = delta(tmp_path, external=True)
    change(memory, lambda v: v["external_artifacts"][0].update(uri=uri))
    with pytest.raises(CapsuleError, match="URI"):
        extend_capsule(
            parent, LocalFileAdapter(memory), Goal("Evolve", ("evolution",)), tmp_path / "child"
        )


@pytest.mark.parametrize("version", [[], {}, None, "2.0"])
def test_malformed_or_unknown_version_rejected(capsule, version):
    path = capsule / "manifest.json"
    value = json.loads(path.read_text())
    value["schema_version"] = version
    path.write_text(json.dumps(value))
    with pytest.raises(CapsuleError, match="Unsupported schema version"):
        inspect_capsule(capsule)
