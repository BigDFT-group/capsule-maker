"""Capsule assembly and safe transfer. No imported code is executed here."""

from __future__ import annotations

import json
import os
import platform
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from importlib import metadata, resources
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import InvalidSpecifier, SpecifierSet

from .adapters import MemoryAdapter

MAX_FILES = 200
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_TOTAL_BYTES = 50 * 1024 * 1024
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
SCHEMA_VERSION = "1.0"


class CapsuleError(ValueError):
    """An invalid, unsafe, incomplete, or incompatible research object."""


@dataclass(frozen=True)
class Goal:
    objective: str
    tags: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict:
        return {"objective": self.objective, "tags": list(self.tags)}


def canonical(value: dict) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def schema(name: str = "capsule") -> dict:
    return json.loads(
        resources.files("capsule_maker")
        .joinpath(f"schemas/{name}-v1.schema.json")
        .read_text()
    )


def validate_schema(value: dict, name: str = "capsule") -> None:
    errors = sorted(
        Draft202012Validator(schema(name)).iter_errors(value), key=lambda e: str(e.path)
    )
    if errors:
        error = errors[0]
        # Avoid echoing secret-bearing values in validation messages.
        raise CapsuleError(
            f"Invalid {name} schema at {'/'.join(map(str, error.path)) or '<root>'}: "
            f"{error.validator} constraint"
        )


def valid_path(name: str) -> str:
    """Use portable, unambiguous relative file names, including on Windows."""
    if not isinstance(name, str) or not name or "\\" in name:
        raise CapsuleError("Unsafe file path")
    parts = name.split("/")
    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if (
        PurePosixPath(name).is_absolute()
        or len(name) > 240
        or any(
            not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", p)
            or p.endswith(".")
            or p.split(".")[0].upper() in reserved
            for p in parts
        )
    ):
        raise CapsuleError("Unsafe or nonportable file path")
    return name


def safe_path(root: Path, name: str) -> Path:
    valid_path(name)
    root = Path(root)
    if root.is_symlink():
        raise CapsuleError("Symlink root is not permitted")
    target = root
    for part in name.split("/"):
        target = target / part
        if target.is_symlink():
            raise CapsuleError("Symlink file or directory is not permitted")
    return target


def read_bytes(path: Path, limit: int = MAX_FILE_BYTES) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise CapsuleError(f"Missing or unsafe file: {path.name}")
    if path.stat().st_size > limit:
        raise CapsuleError("File exceeds size limit")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise CapsuleError("File exceeds size limit")
    return data


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CapsuleError("Duplicate JSON key")
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    try:
        return json.loads(
            read_bytes(path, MAX_MANIFEST_BYTES),
            object_pairs_hook=_unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(
                CapsuleError("Nonfinite JSON number")
            ),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise CapsuleError("Invalid UTF-8 JSON") from exc


_SECRET_PATTERNS = (
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
    r"\bAKIA[A-Z0-9]{16}\b",
    r"\bsk-[A-Za-z0-9_-]{20,}\b",
    r"(?i)\b(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\b[\"']?\s*[:=]\s*[\"']?[^\s\"',;}{]{8,}",
    r"(?i)\bauthorization\s*[:=]\s*[\"']?bearer\s+[^\s\"']{8,}",
    r"[a-zA-Z][a-zA-Z0-9+.-]*://[^/\s:@]+:[^/\s@]+@",
)


def scan_secrets(data: bytes, label: str) -> None:
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise CapsuleError(
            f"Only inspectable UTF-8 artifacts supported: {label}"
        ) from exc
    if any(re.search(pattern, text) for pattern in _SECRET_PATTERNS):
        raise CapsuleError(
            f"Likely secret detected in {label}; remove it before transfer"
        )


def _index(items: list[dict], key: str) -> dict:
    result = {item[key]: item for item in items}
    if len(result) != len(items):
        raise CapsuleError(f"Duplicate {key}")
    return result


def _requirements(deps: dict) -> None:
    try:
        SpecifierSet(deps["python"])
        for text in deps["packages"]:
            req = Requirement(text)
            if req.url or req.extras or req.marker or not str(req.specifier):
                raise CapsuleError(
                    "Dependencies must be named packages with version constraints"
                )
    except (InvalidRequirement, InvalidSpecifier) as exc:
        raise CapsuleError("Invalid dependency declaration") from exc


def _references(records: list[dict], sources: list[dict], artifacts: set[str]) -> None:
    ids = _index(records, "id")
    source_ids = _index(sources, "id")
    for rec in records:
        if rec["sensitive"]:
            raise CapsuleError(
                "Selected sensitive record must be excluded before assembly"
            )
        if not rec["provenance"] or not set(rec["provenance"]) <= source_ids.keys():
            raise CapsuleError(f"Missing provenance for record {rec['id']}")
        for name in ("references", "evidence", "supersedes", "contradicts"):
            if not set(rec[name]) <= ids.keys() or rec["id"] in rec[name]:
                raise CapsuleError(f"Invalid {name} for record {rec['id']}")
        if not set(rec["artifacts"]) <= artifacts:
            raise CapsuleError(f"Missing artifact for record {rec['id']}")
        if (
            rec["status"] == "verified"
            and rec["kind"] != "evidence"
            and not rec["evidence"]
        ):
            raise CapsuleError(f"Verified record lacks evidence: {rec['id']}")
        for evidence_id in rec["evidence"]:
            evidence = ids[evidence_id]
            if (
                evidence["kind"] != "evidence"
                or evidence["status"] != "verified"
                or not evidence["artifacts"]
            ):
                raise CapsuleError(
                    f"Evidence must reference packaged evidence: {evidence_id}"
                )
        if rec["kind"] == "correction" and not rec["supersedes"]:
            raise CapsuleError("Correction must link the superseded decision")
        for older in rec["supersedes"]:
            if ids[older]["status"] != "superseded":
                raise CapsuleError("Superseded record must have superseded status")

    # Use an explicit stack: valid long histories must not hit Python's recursion limit.
    visited, active = set(), set()
    for start in ids:
        stack = [(start, False)]
        while stack:
            record_id, leaving = stack.pop()
            if leaving:
                active.remove(record_id)
                visited.add(record_id)
                continue
            if record_id in active:
                raise CapsuleError("Cyclic supersession history")
            if record_id in visited:
                continue
            active.add(record_id)
            stack.append((record_id, True))
            stack.extend((older, False) for older in ids[record_id]["supersedes"])


def conflicts(records: list[dict]) -> list[dict]:
    """Report explicit conflicts and incompatible active assertions on a claim key."""
    result = {}
    ids = _index(records, "id")
    for rec in records:
        for other in rec["contradicts"]:
            left, right = sorted((rec["id"], other))
            result[(left, right)] = {
                "left": left,
                "right": right,
                "reason": "explicit contradiction",
            }
        if rec.get("claim_key") and rec["status"] != "superseded":
            for other in ids.values():
                if (
                    other["id"] != rec["id"]
                    and other.get("claim_key") == rec["claim_key"]
                    and other["status"] != "superseded"
                    and other["content"] != rec["content"]
                ):
                    left, right = sorted((rec["id"], other["id"]))
                    result[(left, right)] = {
                        "left": left,
                        "right": right,
                        "reason": "different active assertions on claim_key",
                    }
    return [result[key] for key in sorted(result)]


def select(snapshot: dict, goal: Goal) -> list[dict]:
    validate_schema(snapshot, "memory")
    if not goal.objective.strip():
        raise CapsuleError("An explicit research objective is required")
    ids = _index(snapshot["records"], "id")
    tags = {tag.casefold() for tag in goal.tags}
    stop = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "into",
        "required",
        "create",
        "capsule",
        "containing",
        "everything",
        "including",
        "continue",
        "research",
    }
    terms = set(re.findall(r"[a-z0-9]+", goal.objective.casefold())) - stop
    chosen = set()
    for rec in ids.values():
        if tags:
            match = tags.intersection(tag.casefold() for tag in rec["tags"])
        else:
            words = set(
                re.findall(
                    r"[a-z0-9]+",
                    (" ".join(rec["tags"]) + " " + rec["content"]).casefold(),
                )
            )
            match = terms.intersection(words)
        if match:
            chosen.add(rec["id"])
    if not chosen:
        raise CapsuleError("No records match the goal; supply explicit matching tags")
    changed = True
    while changed:
        before = set(chosen)
        for record_id in list(chosen):
            rec = ids[record_id]
            for name in ("references", "evidence", "supersedes", "contradicts"):
                for target in rec[name]:
                    if target not in ids:
                        raise CapsuleError(f"Missing required record: {target}")
                    chosen.add(target)
        # Carry corrections and explicit conflicts even when they have different tags.
        for rec in ids.values():
            if chosen.intersection(rec["supersedes"] + rec["contradicts"]):
                chosen.add(rec["id"])
        keys = {ids[i].get("claim_key") for i in chosen} - {None}
        chosen.update(r["id"] for r in ids.values() if r.get("claim_key") in keys)
        changed = before != chosen
    return [ids[i] for i in sorted(chosen)]


def review_digest(manifest: dict) -> str:
    content = dict(manifest)
    content["review"] = None
    return sha256(canonical(content)).hexdigest()


def summary(manifest: dict) -> str:
    lines = [
        "# Research Capsule",
        "",
        manifest["goal"]["objective"],
        "",
        f"Origin: {manifest['origin']['backend']} — {manifest['origin']['description']}",
        "",
        "## Knowledge",
        "",
    ]
    for rec in manifest["records"]:
        lines += [
            f"### {rec['id']} ({rec['kind']}, {rec['status']})",
            "",
            rec["content"],
            "",
            f"Evidence: {', '.join(rec['evidence']) or 'none'}",
            f"Provenance: {', '.join(rec['provenance'])}",
            f"Supersedes: {', '.join(rec['supersedes']) or 'none'}",
            "",
        ]
    lines += ["## Source references", ""]
    lines += [
        f"- {s['id']}: {s['uri']} — {s['description']}" for s in manifest["sources"]
    ]
    lines += ["", "## Conflicts", ""]
    lines += [
        f"- {c['left']} ↔ {c['right']}: {c['reason']}" for c in manifest["conflicts"]
    ] or ["None declared or detected."]
    lines += ["", "## Environment", "", f"Python {manifest['dependencies']['python']}"]
    lines += [f"- {p}" for p in manifest["dependencies"]["packages"]]
    lines += [
        "",
        "## Receiving instructions",
        "",
        "Inspect the manifest, knowledge, evidence, procedures, and tests before approval.",
        "Verify integrity and environment requirements. Import/inspection never run code.",
        "Run tests only after explicit trust using `capsule-maker verify PATH --trust-code`.",
        "Checksums establish integrity, not authorship or scientific validity.",
        "",
    ]
    return "\n".join(lines)


def _write_manifest(root: Path, value: dict) -> None:
    data = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=root, delete=False
    ) as f:
        temp = Path(f.name)
        f.write(data)
    try:
        temp.replace(root / "manifest.json")
    finally:
        temp.unlink(missing_ok=True)


def _destination(destination: str | Path) -> Path:
    path = Path(destination).absolute()
    if path.exists() or path.is_symlink():
        raise CapsuleError("Destination must not exist")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def create_capsule(adapter: MemoryAdapter, goal: Goal, destination: str | Path) -> dict:
    snapshot = adapter.snapshot()
    selected = select(snapshot, goal)
    descriptors = _index(snapshot["artifacts"], "path")
    names = {name for rec in selected for name in rec["artifacts"]}
    if not names <= descriptors.keys():
        raise CapsuleError("Missing required artifact descriptor")
    source_ids = {source for rec in selected for source in rec["provenance"]}
    all_sources = _index(snapshot["sources"], "id")
    if not source_ids <= all_sources.keys():
        raise CapsuleError("Missing required source")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "origin": snapshot["origin"],
        "goal": goal.as_dict(),
        "records": selected,
        "sources": [all_sources[i] for i in sorted(source_ids)],
        "dependencies": {
            "python": snapshot["python"],
            "packages": sorted(
                {p for name in names for p in descriptors[name]["packages"]}
            ),
        },
        "inventory": [],
        "conflicts": conflicts(selected),
        "review": None,
    }
    _references(selected, manifest["sources"], names)
    _requirements(manifest["dependencies"])
    scan_secrets(canonical(manifest), "metadata")
    destination = _destination(destination)
    with tempfile.TemporaryDirectory(prefix="capsule-", dir=destination.parent) as temp:
        stage = Path(temp) / "payload"
        stage.mkdir()
        contents = {}
        for name in sorted(names):
            valid_path(name)
            if name.casefold() in {"manifest.json", "summary.md"}:
                raise CapsuleError("Reserved artifact path")
            contents[name] = (adapter.read_artifact(name), descriptors[name]["role"])
        contents["SUMMARY.md"] = (summary(manifest).encode(), "summary")
        if (
            len(contents) + 1 > MAX_FILES
            or sum(len(v[0]) for v in contents.values()) > MAX_TOTAL_BYTES
        ):
            raise CapsuleError("Capsule exceeds inventory limits")
        for name, (data, role) in contents.items():
            if len(data) > MAX_FILE_BYTES:
                raise CapsuleError("Artifact exceeds size limit")
            scan_secrets(data, name)
            path = safe_path(stage, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            manifest["inventory"].append(
                {
                    "path": name,
                    "role": role,
                    "sha256": sha256(data).hexdigest(),
                    "size": len(data),
                }
            )
        validate_schema(manifest)
        _write_manifest(stage, manifest)
        inspect_capsule(stage)
        stage.rename(destination)
    return manifest


def inspect_capsule(directory: str | Path) -> dict:
    """Check structure, references, secrets and hashes, then return JSON metadata."""
    root = Path(directory)
    if root.is_symlink() or not root.is_dir():
        raise CapsuleError("Capsule must be a regular directory")
    manifest = read_json(safe_path(root, "manifest.json"))
    validate_schema(manifest)
    _requirements(manifest["dependencies"])
    scan_secrets(canonical(manifest), "metadata")
    inventory = _index(manifest["inventory"], "path")
    if len(inventory) + 1 > MAX_FILES:
        raise CapsuleError("Too many files")
    expected = set(inventory) | {"manifest.json"}
    if len({p.casefold() for p in expected}) != len(expected):
        raise CapsuleError("Ambiguous file paths")
    if "manifest.json" in inventory:
        raise CapsuleError("Manifest cannot inventory itself")
    actual = set()
    total = 0
    # Refuse symlinks and undeclared files; do not follow symlink directories.
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(parent) / name
            if path.is_symlink():
                raise CapsuleError("Symlinks are not permitted")
        for name in files:
            relative = (Path(parent) / name).relative_to(root).as_posix()
            actual.add(valid_path(relative))
            if len(actual) > MAX_FILES:
                raise CapsuleError("Too many files")
    if actual != expected:
        raise CapsuleError("Inventory mismatch: missing or undeclared files")
    for name, descriptor in inventory.items():
        data = read_bytes(safe_path(root, name))
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise CapsuleError("Capsule exceeds total size limit")
        if (
            len(data) != descriptor["size"]
            or sha256(data).hexdigest() != descriptor["sha256"]
        ):
            raise CapsuleError(f"Integrity failure: {name}")
        scan_secrets(data, name)
    _references(manifest["records"], manifest["sources"], set(inventory))
    if manifest["conflicts"] != conflicts(manifest["records"]):
        raise CapsuleError("Conflict report does not match records")
    if manifest["review"] and manifest["review"]["digest"] != review_digest(manifest):
        raise CapsuleError("Approval is stale: content changed after review")
    return manifest


def approve_capsule(directory: str | Path, reviewer: str) -> dict:
    """Record the caller's human review decision, bound to this exact inventory."""
    if not reviewer.strip():
        raise CapsuleError("Reviewer identity is required")
    manifest = inspect_capsule(directory)
    if manifest["conflicts"]:
        raise CapsuleError(
            "Resolve or explicitly supersede contradictions before approval"
        )
    manifest["review"] = {
        "reviewer": reviewer,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "digest": review_digest(manifest),
    }
    scan_secrets(canonical(manifest), "metadata")
    _write_manifest(Path(directory), manifest)
    return manifest


def export_capsule(directory: str | Path, archive: str | Path) -> Path:
    manifest = inspect_capsule(directory)
    if not manifest["review"]:
        raise CapsuleError(
            "Explicit content review and approval required before export"
        )
    destination = _destination(archive)
    root = Path(directory)
    with tempfile.TemporaryDirectory(
        prefix="capsule-export-", dir=destination.parent
    ) as temp:
        path = Path(temp) / "capsule.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as stream:
            for name in sorted(
                ["manifest.json"] + [i["path"] for i in manifest["inventory"]]
            ):
                data = read_bytes(safe_path(root, name))
                scan_secrets(data, name)
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                stream.writestr(info, data)
        # Verify the actual bytes exported, not just the pre-export directory.
        import_capsule(path, Path(temp) / "check")
        os.link(
            path, destination
        )  # atomic no-overwrite publication on the same filesystem
    return destination


def import_capsule(archive: str | Path, destination: str | Path) -> dict:
    """Extract only bounded regular UTF-8 files; never import or execute Python."""
    destination = _destination(destination)
    if Path(archive).is_symlink() or not Path(archive).is_file():
        raise CapsuleError("Archive must be a regular file")
    if Path(archive).stat().st_size > MAX_TOTAL_BYTES:
        raise CapsuleError("Archive exceeds size limit")
    try:
        with tempfile.TemporaryDirectory(
            prefix="capsule-import-", dir=destination.parent
        ) as temp:
            stage = Path(temp) / "payload"
            stage.mkdir()
            with zipfile.ZipFile(archive) as stream:
                entries = stream.infolist()
                if not entries or len(entries) > MAX_FILES:
                    raise CapsuleError("Invalid archive file count")
                seen = set()
                total = 0
                for entry in entries:
                    name = valid_path(entry.filename)
                    mode = (entry.external_attr >> 16) & 0o170000
                    if (
                        name.casefold() in seen
                        or entry.is_dir()
                        or mode not in (0, stat.S_IFREG)
                        or entry.flag_bits & 1
                    ):
                        raise CapsuleError(
                            "Duplicate, encrypted, or nonregular archive entry"
                        )
                    seen.add(name.casefold())
                    total += entry.file_size
                    if entry.file_size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                        raise CapsuleError("Archive exceeds extracted size limits")
                    with stream.open(entry) as source:
                        data = source.read(MAX_FILE_BYTES + 1)
                    if len(data) != entry.file_size:
                        raise CapsuleError("Archive entry size mismatch")
                    scan_secrets(data, name)
                    target = safe_path(stage, name)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
            manifest = inspect_capsule(stage)
            if not manifest["review"]:
                raise CapsuleError("Transferred capsule lacks export approval")
            stage.rename(destination)
            return manifest
    except (
        zipfile.BadZipFile,
        RuntimeError,
        NotImplementedError,
        OSError,
        zlib.error,
        EOFError,
    ) as exc:
        raise CapsuleError("Invalid or unreadable archive") from exc


def check_environment(manifest: dict) -> dict:
    _requirements(manifest["dependencies"])
    problems = []
    deps = manifest["dependencies"]
    if platform.python_version() not in SpecifierSet(deps["python"]):
        problems.append(
            f"Python {platform.python_version()} does not satisfy {deps['python']}"
        )
    installed = {}
    for text in deps["packages"]:
        req = Requirement(text)
        try:
            version = metadata.version(req.name)
            installed[req.name] = version
            if version not in req.specifier:
                problems.append(
                    f"{req.name} {version} does not satisfy {req.specifier}"
                )
        except metadata.PackageNotFoundError:
            problems.append(f"Missing dependency: {req.name} {req.specifier}")
    return {
        "compatible": not problems,
        "problems": problems,
        "installed": installed,
        "python": platform.python_version(),
    }


def verify_capsule(
    directory: str | Path,
    *,
    environment: bool = True,
    trust_code: bool = False,
    timeout: float = 60,
) -> dict:
    """Integrity and environment verification; tests require explicit trust.

    Trusted execution uses a disposable copy to keep the capsule immutable.
    This is NOT a sandbox: trusted code has the caller's OS privileges.
    """
    manifest = inspect_capsule(directory)
    result = {"integrity": True, "conflicts": manifest["conflicts"], "tests": "not run"}
    if environment or trust_code:
        result["environment"] = check_environment(manifest)
        if not result["environment"]["compatible"]:
            raise CapsuleError(
                "Incompatible environment: "
                + "; ".join(result["environment"]["problems"])
            )
    if trust_code:
        if manifest["conflicts"]:
            raise CapsuleError("Resolve contradictions before trusted validation")
        if not any(
            i["role"] == "test"
            and i["path"].startswith("tests/")
            and i["path"].endswith(".py")
            for i in manifest["inventory"]
        ):
            raise CapsuleError("No bundled regression tests in tests/")
        with tempfile.TemporaryDirectory(prefix="capsule-validation-") as temp:
            work = Path(temp)
            for entry in manifest["inventory"]:
                target = safe_path(work, entry["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(
                    read_bytes(safe_path(Path(directory), entry["path"]))
                )
            env = {
                k: v
                for k, v in os.environ.items()
                if k not in {"PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"}
            }
            # unittest avoids dependence on pytest and any host pytest plugins.
            command = [
                sys.executable,
                "-B",
                "-c",
                "import sys,unittest; sys.path.insert(0,'.'); "
                "suite=unittest.defaultTestLoader.discover('tests'); "
                "result=unittest.TextTestRunner(verbosity=2).run(suite); "
                "sys.exit(0 if result.wasSuccessful() and result.testsRun else 1)",
            ]
            try:
                run = subprocess.run(
                    command,
                    cwd=work,
                    env=env,
                    text=True,
                    capture_output=True,
                    timeout=timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise CapsuleError("Trusted regression tests timed out") from exc
            if run.returncode:
                raise CapsuleError(
                    "Trusted regression tests failed: " + run.stdout + run.stderr
                )
            result["tests"] = "passed"
            result["test_output"] = run.stdout + run.stderr
    return result


def resume_knowledge(directory: str | Path, goal: Goal | None = None) -> dict:
    manifest = inspect_capsule(directory)
    records = manifest["records"]
    if goal:
        snapshot = {
            "format_version": "1.0",
            "origin": manifest["origin"],
            "records": records,
            "sources": manifest["sources"],
            "python": manifest["dependencies"]["python"],
            "artifacts": [],
        }
        records = select(snapshot, goal)
    return {
        "goal": manifest["goal"],
        "records": records,
        "sources": manifest["sources"],
        "conflicts": conflicts(records),
        "dependencies": manifest["dependencies"],
    }


def retrieve_content(directory: str | Path, path: str) -> str:
    manifest = inspect_capsule(directory)
    if path not in {i["path"] for i in manifest["inventory"]}:
        raise CapsuleError("Content path is not in inventory")
    return read_bytes(safe_path(Path(directory), path)).decode("utf-8")
