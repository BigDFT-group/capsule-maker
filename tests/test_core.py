import json
import subprocess
import sys

import pytest
from jsonschema import Draft202012Validator

from capsule_maker import (
    CapsuleError,
    Goal,
    LocalFileAdapter,
    MemoryAdapter,
    approve_capsule,
    check_environment,
    create_capsule,
    export_capsule,
    import_capsule,
    inspect_capsule,
    resume_knowledge,
    retrieve_content,
    select,
    verify_capsule,
)
from capsule_maker.core import schema


def modify_memory(memory, change):
    value = json.loads(memory.read_text())
    change(value)
    memory.write_text(json.dumps(value))
    return value


def write_manifest(capsule, change):
    path = capsule / "manifest.json"
    value = json.loads(path.read_text())
    change(value)
    path.write_text(json.dumps(value))


def test_create_schema_and_evidence(capsule):
    manifest = inspect_capsule(capsule)
    Draft202012Validator(schema()).validate(manifest)
    records = {r["id"]: r for r in manifest["records"]}
    assert {
        "correct-sign",
        "wrong-sign",
        "numerical-evidence",
        "problem",
    } <= records.keys()
    assert records["wrong-sign"]["status"] == "superseded"
    assert records["correct-sign"]["supersedes"] == ["wrong-sign"]
    assert records["validated-solver"]["evidence"] == ["numerical-evidence"]
    assert manifest["sources"][0]["uri"].startswith("urn:")
    assert manifest["dependencies"]["packages"] == ["numpy>=1.26,<3"]
    assert "Supersedes: wrong-sign" in (capsule / "SUMMARY.md").read_text()
    assert "unrelated" not in records
    assert "generalization" not in records


def test_goal_selection(memory, tmp_path):
    adapter = LocalFileAdapter(memory)
    results = select(adapter.snapshot(), Goal("Literature reading", ("literature",)))
    assert [r["id"] for r in results] == ["unrelated"]
    natural = select(adapter.snapshot(), Goal("numerical convergence study"))
    assert "validated-solver" in {r["id"] for r in natural}
    hypothesis = select(adapter.snapshot(), Goal("Future forcing", ("future-forcing",)))
    assert hypothesis[0]["status"] == "hypothesis"
    with pytest.raises(CapsuleError, match="No records match"):
        select(adapter.snapshot(), Goal("Other goal", ("nonexistent",)))
    with pytest.raises(CapsuleError, match="explicit research objective"):
        select(adapter.snapshot(), Goal(" "))
    create_capsule(
        adapter, Goal("Literature", ("literature",)), tmp_path / "literature"
    )
    assert inspect_capsule(tmp_path / "literature")["dependencies"]["packages"] == []


def test_abstract_adapter_and_backend_independence(memory, tmp_path):
    with pytest.raises(TypeError):
        MemoryAdapter()
    local = LocalFileAdapter(memory)

    class SnapshotAdapter(MemoryAdapter):
        def snapshot(self):
            value = local.snapshot()
            value["origin"]["backend"] = "test-independent-memory"
            return value

        def read_artifact(self, path):
            return local.read_artifact(path)

    manifest = create_capsule(
        SnapshotAdapter(), Goal("Poisson", ("poisson",)), tmp_path / "neutral"
    )
    assert manifest["origin"]["backend"] == "test-independent-memory"


def test_roundtrip_approval_required(capsule, tmp_path):
    archive = tmp_path / "capsule.zip"
    with pytest.raises(CapsuleError, match="review and approval"):
        export_capsule(capsule, archive)
    assert not archive.exists()
    approved = approve_capsule(capsule, "researcher")
    export_capsule(capsule, archive)
    restored = import_capsule(archive, tmp_path / "restored")
    assert restored == approved
    for item in approved["inventory"]:
        name = item["path"]
        assert (capsule / name).read_bytes() == (
            tmp_path / "restored" / name
        ).read_bytes()
    assert verify_capsule(tmp_path / "restored")["tests"] == "not run"


def test_stale_approval(capsule):
    approve_capsule(capsule, "reviewer")
    write_manifest(
        capsule, lambda value: value["goal"].update(objective="Changed objective")
    )
    with pytest.raises(CapsuleError, match="stale"):
        inspect_capsule(capsule)


def test_conflicts_are_reported_and_block_approval(memory, tmp_path):
    def change(value):
        alternative = dict(value["records"][3])
        alternative.update(
            id="alternative",
            kind="decision",
            content="Use the opposite sign",
            supersedes=[],
            tags=["unmatched"],
            contradicts=["correct-sign"],
        )
        value["records"].append(alternative)

    modify_memory(memory, change)
    root = tmp_path / "conflict"
    manifest = create_capsule(
        LocalFileAdapter(memory), Goal("Convergence", ("convergence",)), root
    )
    assert manifest["conflicts"]
    assert "alternative" in {r["id"] for r in manifest["records"]}
    assert "alternative" in (root / "SUMMARY.md").read_text()
    with pytest.raises(CapsuleError, match="contradictions"):
        approve_capsule(root, "reviewer")


def test_claim_key_conflict_without_explicit_link(memory, tmp_path):
    def change(value):
        alternative = dict(value["records"][3])
        alternative.update(
            id="alternative",
            kind="decision",
            content="Different active claim",
            supersedes=[],
            tags=[],
        )
        value["records"].append(alternative)

    modify_memory(memory, change)
    manifest = create_capsule(
        LocalFileAdapter(memory),
        Goal("Convergence", ("convergence",)),
        tmp_path / "conflict",
    )
    assert (
        manifest["conflicts"][0]["reason"] == "different active assertions on claim_key"
    )


@pytest.mark.parametrize(
    "change,expected",
    [
        (lambda v: v["records"][4]["evidence"].clear(), "lacks evidence"),
        (
            lambda v: v["records"][4]["references"].append("absent"),
            "Missing required record",
        ),
        (
            lambda v: v["records"][4]["artifacts"].append("absent.py"),
            "artifact descriptor",
        ),
        (lambda v: v["records"][4]["provenance"].append("absent"), "required source"),
        (lambda v: v["records"][3]["supersedes"].clear(), "Correction must link"),
        (lambda v: v["records"][2].update(status="unverified"), "superseded status"),
        (lambda v: v["records"].append(dict(v["records"][0])), "Duplicate id"),
        (lambda v: v.update(format_version="2.0"), "schema"),
    ],
)
def test_incomplete_memory_fails_closed(memory, tmp_path, change, expected):
    modify_memory(memory, change)
    target = tmp_path / "broken"
    with pytest.raises(CapsuleError, match=expected):
        create_capsule(
            LocalFileAdapter(memory), Goal("Convergence", ("convergence",)), target
        )
    assert not target.exists()


def test_missing_artifact(memory, tmp_path):
    (memory.parent / "solver.py").unlink()
    with pytest.raises(CapsuleError, match="Missing or unsafe file"):
        create_capsule(
            LocalFileAdapter(memory),
            Goal("Convergence", ("convergence",)),
            tmp_path / "broken",
        )


def test_environment_checks(capsule):
    manifest = inspect_capsule(capsule)
    assert check_environment(manifest)["compatible"]
    manifest["dependencies"]["packages"] = ["capsule-maker-impossible-package>=1"]
    assert "Missing dependency" in check_environment(manifest)["problems"][0]
    manifest["dependencies"]["packages"] = ["numpy<0.1"]
    assert not check_environment(manifest)["compatible"]
    manifest["dependencies"]["packages"] = []
    manifest["dependencies"]["python"] = ">=99"
    assert not check_environment(manifest)["compatible"]
    write_manifest(capsule, lambda v: v["dependencies"].update(python=">=99"))
    with pytest.raises(CapsuleError, match="Incompatible environment"):
        verify_capsule(capsule)
    assert verify_capsule(capsule, environment=False)["integrity"]


@pytest.mark.parametrize(
    "requirement",
    [
        "numpy @ https://example.org/code.whl",
        "numpy",
        "numpy[extra]>=1",
        "numpy>=1; python_version>'3'",
    ],
)
def test_dependency_contract(capsule, requirement):
    write_manifest(capsule, lambda v: v["dependencies"].update(packages=[requirement]))
    with pytest.raises(CapsuleError, match="Dependencies must"):
        inspect_capsule(capsule)


def test_retrieve_and_resume(capsule):
    resumed = resume_knowledge(capsule, Goal("Convergence", ("convergence",)))
    assert "correct-sign" in {r["id"] for r in resumed["records"]}
    assert "solve_poisson" in retrieve_content(capsule, "solver.py")
    with pytest.raises(CapsuleError, match="not in inventory"):
        retrieve_content(capsule, "memory.json")


def test_cli_commands(capsule, tmp_path):
    def call(*args):
        return subprocess.run(
            [sys.executable, "-m", "capsule_maker.cli", *map(str, args)],
            text=True,
            capture_output=True,
        )

    assert call("inspect", capsule).returncode == 0
    assert call("contents", capsule, "--path", "solver.py").returncode == 0
    assert (
        call(
            "resume", capsule, "--goal", "Convergence", "--tag", "convergence"
        ).returncode
        == 0
    )
    run = call("export", capsule, tmp_path / "blocked.zip")
    assert run.returncode == 2
    assert "approval" in run.stderr
    assert call("approve", capsule, "--reviewer", "cli-reviewer").returncode == 0
    assert call("export", capsule, tmp_path / "cli.zip").returncode == 0
    assert (
        call("import", tmp_path / "cli.zip", tmp_path / "cli-imported").returncode == 0
    )
    assert call("verify", tmp_path / "cli-imported", "--trust-code").returncode == 0


def test_verified_claim_requires_verified_evidence(memory, tmp_path):
    modify_memory(memory, lambda v: v["records"][5].update(status="unverified"))
    with pytest.raises(CapsuleError, match="Evidence must reference"):
        create_capsule(
            LocalFileAdapter(memory),
            Goal("Convergence", ("convergence",)),
            tmp_path / "invalid",
        )


def test_cyclic_supersession_rejected(memory, tmp_path):
    def change(v):
        v["records"][3]["status"] = "superseded"
        v["records"][2]["supersedes"] = ["correct-sign"]

    modify_memory(memory, change)
    with pytest.raises(CapsuleError, match="Cyclic supersession"):
        create_capsule(
            LocalFileAdapter(memory),
            Goal("Convergence", ("convergence",)),
            tmp_path / "cyclic",
        )


def test_long_correction_history_does_not_require_recursive_execution():
    from capsule_maker.core import _references

    records = [
        {
            "id": str(i),
            "kind": "decision",
            "status": "superseded",
            "sensitive": False,
            "provenance": ["source"],
            "references": [],
            "evidence": [],
            "artifacts": [],
            "supersedes": [str(i + 1)] if i < 1099 else [],
            "contradicts": [],
        }
        for i in range(1100)
    ]
    _references(records, [{"id": "source"}], set())
