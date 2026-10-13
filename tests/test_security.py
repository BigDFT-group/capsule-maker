import json
import stat
import zipfile
from hashlib import sha256

import pytest

from capsule_maker import (
    CapsuleError,
    Goal,
    LocalFileAdapter,
    approve_capsule,
    create_capsule,
    export_capsule,
    import_capsule,
    inspect_capsule,
    verify_capsule,
)
from capsule_maker.core import scan_secrets


@pytest.mark.parametrize(
    "name",
    [
        "../escape.py",
        "/absolute",
        "C:/windows",
        "folder/../escape",
        "a\\b",
        "a//b",
        "./a",
        "a/.",
        "CON.txt",
        "a.",
        "a:b",
        ".hidden",
    ],
)
def test_unsafe_archive_paths(tmp_path, name):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr(name, "danger")
    target = tmp_path / "imported"
    with pytest.raises(CapsuleError, match="path"):
        import_capsule(archive, target)
    assert not target.exists()
    assert not (tmp_path / "escape.py").exists()


def test_zip_symlink(tmp_path):
    path = tmp_path / "symlink.zip"
    with zipfile.ZipFile(path, "w") as z:
        item = zipfile.ZipInfo("solver.py")
        item.create_system = 3
        item.external_attr = (stat.S_IFLNK | 0o777) << 16
        z.writestr(item, "/etc/passwd")
    with pytest.raises(CapsuleError, match="nonregular"):
        import_capsule(path, tmp_path / "target")


def test_duplicate_archive_paths(tmp_path):
    path = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("solver.py", "one")
        z.writestr("SOLVER.py", "two")
    with pytest.raises(CapsuleError, match="Duplicate"):
        import_capsule(path, tmp_path / "target")


def test_archive_size_limit(tmp_path, monkeypatch):
    import capsule_maker.core as core

    path = tmp_path / "large.zip"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("large.txt", "a" * 1000)
    monkeypatch.setattr(core, "MAX_FILE_BYTES", 100)
    with pytest.raises(CapsuleError, match="size limits"):
        import_capsule(path, tmp_path / "target")


def test_corrupt_zip(tmp_path):
    path = tmp_path / "corrupt.zip"
    path.write_bytes(b"not a zip")
    with pytest.raises(CapsuleError, match="Invalid or unreadable archive"):
        import_capsule(path, tmp_path / "target")


def test_inventory_corruption(capsule, tmp_path):
    approve_capsule(capsule, "reviewer")
    (capsule / "solver.py").write_text("modified")
    with pytest.raises(CapsuleError, match="Integrity failure"):
        export_capsule(capsule, tmp_path / "corrupt.zip")
    assert not (tmp_path / "corrupt.zip").exists()


def test_corrupted_archive_content(capsule, tmp_path):
    approve_capsule(capsule, "reviewer")
    good = export_capsule(capsule, tmp_path / "good.zip")
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(good) as source, zipfile.ZipFile(bad, "w") as target:
        for name in source.namelist():
            target.writestr(
                name, "corruption" if name == "solver.py" else source.read(name)
            )
    with pytest.raises(CapsuleError, match="Integrity failure"):
        import_capsule(bad, tmp_path / "broken")
    assert not (tmp_path / "broken").exists()


@pytest.mark.parametrize(
    "mutation", ["missing", "extra", "symlink", "version", "binary"]
)
def test_invalid_directory(capsule, mutation, tmp_path):
    if mutation == "missing":
        (capsule / "results.json").unlink()
    elif mutation == "extra":
        (capsule / "extra.py").write_text("# undeclared")
    elif mutation == "symlink":
        (capsule / "solver.py").unlink()
        (capsule / "solver.py").symlink_to(tmp_path / "outside")
    elif mutation == "version":
        manifest = json.loads((capsule / "manifest.json").read_text())
        manifest["schema_version"] = "2.0"
        (capsule / "manifest.json").write_text(json.dumps(manifest))
    elif mutation == "binary":
        (capsule / "results.json").write_bytes(b"\xff")
    with pytest.raises(CapsuleError):
        inspect_capsule(capsule)


@pytest.mark.parametrize(
    "secret",
    [
        "api_key='" + "x" * 24 + "'",
        "ghp_" + "a" * 36,
        "sk-" + "b" * 30,
        "AKIA" + "A" * 16,
        "-----BEGIN PRIVATE KEY-----",
        "Authorization: Bearer " + "secret" * 5,
        "https://user:credential@example.org/resource",
    ],
)
def test_secret_detection(secret):
    with pytest.raises(CapsuleError, match="Likely secret") as error:
        scan_secrets(secret.encode(), "test-artifact")
    assert secret not in str(error.value)


def test_secret_export_block_even_with_updated_hash(capsule, tmp_path):
    approve_capsule(capsule, "reviewer")
    data = b"api_key='" + b"x" * 24 + b"'"
    (capsule / "solver.py").write_bytes(data)
    manifest = json.loads((capsule / "manifest.json").read_text())
    item = next(i for i in manifest["inventory"] if i["path"] == "solver.py")
    item.update(sha256=sha256(data).hexdigest(), size=len(data))
    (capsule / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(CapsuleError, match="Likely secret"):
        export_capsule(capsule, tmp_path / "secret.zip")


def test_sensitive_selection_blocked_unrelated_sensitive_excluded(memory, tmp_path):
    value = json.loads(memory.read_text())
    value["records"][-1]["sensitive"] = True
    memory.write_text(json.dumps(value))
    create_capsule(
        LocalFileAdapter(memory),
        Goal("Convergence", ("convergence",)),
        tmp_path / "safe",
    )
    value["records"][3]["sensitive"] = True
    memory.write_text(json.dumps(value))
    with pytest.raises(CapsuleError, match="sensitive"):
        create_capsule(
            LocalFileAdapter(memory),
            Goal("Convergence", ("convergence",)),
            tmp_path / "unsafe",
        )


def test_local_adapter_rejects_path_escape(memory):
    with pytest.raises(CapsuleError, match="path"):
        LocalFileAdapter(memory).read_artifact("../outside")
    (memory.parent / "link.py").symlink_to(memory)
    with pytest.raises(CapsuleError, match="Symlink"):
        LocalFileAdapter(memory).read_artifact("link.py")


def test_import_and_inspection_never_execute_code(memory, tmp_path):
    marker = tmp_path / "executed"
    payload = (
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n"
    )
    (memory.parent / "solver.py").write_text(payload)
    root = tmp_path / "capsule"
    create_capsule(
        LocalFileAdapter(memory), Goal("Convergence", ("convergence",)), root
    )
    approve_capsule(root, "test-reviewer")
    export_capsule(root, tmp_path / "capsule.zip")
    import_capsule(tmp_path / "capsule.zip", tmp_path / "imported")
    assert verify_capsule(tmp_path / "imported")["tests"] == "not run"
    assert not marker.exists()


def test_no_overwrite(capsule, tmp_path):
    approve_capsule(capsule, "reviewer")
    archive = export_capsule(capsule, tmp_path / "capsule.zip")
    with pytest.raises(CapsuleError, match="must not exist"):
        export_capsule(capsule, archive)
    with pytest.raises(CapsuleError, match="must not exist"):
        import_capsule(archive, capsule)


def test_duplicate_json_keys(capsule):
    path = capsule / "manifest.json"
    path.write_text('{"schema_version":"1.0","schema_version":"2.0"}')
    with pytest.raises(CapsuleError, match="Duplicate JSON key"):
        inspect_capsule(capsule)


def test_unapproved_archive_rejected(capsule, tmp_path):
    archive = tmp_path / "unapproved.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for path in capsule.rglob("*"):
            if path.is_file():
                z.write(path, path.relative_to(capsule).as_posix())
    with pytest.raises(CapsuleError, match="lacks export approval"):
        import_capsule(archive, tmp_path / "restored")


def test_adapter_only_serves_declared_artifacts(memory):
    with pytest.raises(CapsuleError, match="not declared"):
        LocalFileAdapter(memory).read_artifact("memory.json")


def test_zip_crc_corruption(capsule, tmp_path):
    approve_capsule(capsule, "reviewer")
    archive = tmp_path / "crc.zip"
    # Stored entry makes the changed byte deterministic and exercises ZIP CRC validation.
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as z:
        for path in capsule.rglob("*"):
            if path.is_file():
                z.write(path, path.relative_to(capsule).as_posix())
    data = bytearray(archive.read_bytes())
    with zipfile.ZipFile(archive) as z:
        item = z.getinfo("solver.py")
        start = item.header_offset + 30 + len(item.filename.encode()) + len(item.extra)
    data[start] ^= 1
    archive.write_bytes(data)
    with pytest.raises(CapsuleError, match="Invalid or unreadable archive"):
        import_capsule(archive, tmp_path / "restored")
