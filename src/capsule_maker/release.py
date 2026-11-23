"""Git-backed distribution with a Git-independent snapshot import."""

import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
import zipfile
import zlib
from pathlib import Path

from .core import (
    MAX_FILE_BYTES,
    MAX_FILES,
    MAX_TOTAL_BYTES,
    CapsuleError,
    _destination,
    export_capsule,
    import_capsule,
    review_digest,
)

LIMITS = {
    "README.md": 64 * 1024,
    "release.json": 64 * 1024,
    "capsule.zip": 50 * 1024**2,
    "capsule.bundle": 50 * 1024**2,
}
PAYLOADS = set(LIMITS) - {"release.json"}
README = """# Capsule handover · release format 1

Without Git, run `capsule-maker import-release RELEASE.zip restored`.
Alternatively, extract capsule.zip and use `capsule-maker import`.
Read SUMMARY.md or run `capsule-maker resume restored`.

For history, extract capsule.bundle and clone it offline with Git.
Check out the exact commit in release.json. Review the bundle source before cloning.
Read and verify the snapshot in isolation from .git using Capsule-Maker.
Continue on a new Git branch and review the new capsule before releasing it.

Inspection and import do not execute the scientific procedures.
"""


def _git(repo, *args, binary=False):
    try:
        result = subprocess.run(
            ["git", "--no-replace-objects", "-C", str(repo), *args],
            capture_output=True,
            check=True,
            timeout=120,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise CapsuleError(f"Git {args[0]} failed; check Git and the local repository") from exc
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _capsule_id(manifest):
    return manifest.get("capsule_id") or "sha256:" + review_digest(manifest)


def create_release(repo, ref, output):
    """Export a local branch of a trusted, dedicated capsule repository."""
    destination = _destination(output)
    branch = "refs/heads/" + ref
    commit = _git(repo, "rev-parse", "--verify", branch)
    if _git(repo, "rev-parse", "--is-shallow-repository") != "false":
        raise CapsuleError("A release requires complete Git history")
    with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
        stage = Path(temp).resolve()
        bundle = stage / "capsule.bundle"
        raw = stage / "files.zip"
        tracked = _git(repo, "ls-tree", "-rlz", commit).rstrip("\0").split("\0")
        if not tracked[0] or len(tracked) > MAX_FILES:
            raise CapsuleError("Invalid capsule commit file count")
        total = 0
        # Read committed bytes directly, without checkout filters or archive attributes.
        with zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as target:
            for record in tracked:
                header, name = record.split("\t", 1)
                mode, kind, oid, size = header.split()
                if mode not in {"100644", "100755"} or kind != "blob":
                    raise CapsuleError("Capsule commit contains a nonregular file")
                total += int(size)
                if int(size) > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                    raise CapsuleError("Capsule commit exceeds size limits")
                target.writestr(name, _git(repo, "cat-file", "blob", oid, binary=True))
        snapshot = stage / "snapshot"
        manifest = import_capsule(raw, snapshot)
        _git(repo, "bundle", "create", str(bundle), branch)
        if _git(repo, "bundle", "list-heads", str(bundle)) != f"{commit} {branch}":
            raise CapsuleError("Git branch moved during release")
        files = {
            "README.md": README.encode(),
            "capsule.zip": export_capsule(snapshot, stage / "capsule.zip").read_bytes(),
        }
        if bundle.stat().st_size > LIMITS["capsule.bundle"]:
            raise CapsuleError("Git bundle exceeds size limit")
        files[bundle.name] = bundle.read_bytes()
        metadata = {
            "release_version": "1",
            "capsule_id": _capsule_id(manifest),
            "git_commit": commit,
            "git_ref": branch,
            "sha256": {name: _sha(data) for name, data in files.items()},
        }
        release = stage / "release.zip"
        with zipfile.ZipFile(release, "w", zipfile.ZIP_DEFLATED) as stream:
            for name, data in files.items():
                stream.writestr(name, data)
            stream.writestr("release.json", json.dumps(metadata, indent=2) + "\n")
        import_release(release, stage / "check")
        os.link(release, destination)
    return metadata


def import_release(archive, destination):
    """Verify the envelope and import its snapshot without invoking Git."""
    destination = _destination(destination)
    archive = Path(archive)
    if not archive.is_file() or archive.is_symlink():
        raise CapsuleError("Release must be a regular file")
    if archive.stat().st_size > sum(LIMITS.values()) + 1024**2:
        raise CapsuleError("Release exceeds size limit")
    try:
        with zipfile.ZipFile(archive) as stream:
            entries = stream.infolist()
            if len(entries) != len(LIMITS) or set(stream.namelist()) != set(LIMITS):
                raise CapsuleError("Unexpected, duplicate, or missing release files")
            for entry in entries:
                if (
                    entry.file_size > LIMITS[entry.filename]
                    or entry.flag_bits & 1
                    or stat.S_IFMT(entry.external_attr >> 16) not in (0, stat.S_IFREG)
                ):
                    raise CapsuleError("Invalid release entry")
            metadata = json.loads(stream.read("release.json"))
            if (
                not isinstance(metadata, dict)
                or metadata.get("release_version") != "1"
                or not re.fullmatch(
                    r"(?:[0-9a-f]{40}|[0-9a-f]{64})", str(metadata.get("git_commit"))
                )
                or not isinstance(metadata.get("sha256"), dict)
                or set(metadata["sha256"]) != PAYLOADS
            ):
                raise CapsuleError("Invalid release metadata or unsupported version")
            with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
                stage = Path(temp)
                for name in sorted(PAYLOADS):
                    data = stream.read(name)
                    if _sha(data) != metadata["sha256"][name]:
                        raise CapsuleError(f"Release checksum mismatch: {name}")
                    if name == "capsule.zip":
                        (stage / name).write_bytes(data)
                manifest = import_capsule(stage / "capsule.zip", stage / "snapshot")
                if _capsule_id(manifest) != metadata.get("capsule_id"):
                    raise CapsuleError("Release capsule ID mismatch")
                _destination(destination)
                (stage / "snapshot").rename(destination)
            return metadata
    except (ValueError, zipfile.BadZipFile, RuntimeError, NotImplementedError, zlib.error) as exc:
        if isinstance(exc, CapsuleError):
            raise
        raise CapsuleError("Invalid or unreadable capsule release") from exc
