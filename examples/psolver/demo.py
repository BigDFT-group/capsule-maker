"""Real C1 -> PSolver investigation -> C2 -> independent consumer (explicit execution)."""

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

from session_b import investigate

from capsule_maker import (
    Goal,
    LocalFileAdapter,
    approve_capsule,
    capsule_size,
    compare_capsules,
    create_capsule,
    export_capsule,
    extend_capsule,
    import_capsule,
    verify_capsule,
    verify_external_artifact,
)


def run(work: Path, backend: str):
    if work.exists():
        raise ValueError("Choose a new output directory")
    work.mkdir(parents=True)
    spec = importlib.util.spec_from_file_location(
        "poisson_session_a", Path(__file__).parents[1] / "poisson/session_a.py"
    )
    session_a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(session_a)
    memory = session_a.generate(work / "session-a-memory")
    c1 = work / "C1"
    create_capsule(LocalFileAdapter(memory), Goal("Continue convergence", ("convergence",)), c1)
    approve_capsule(c1, "deterministic-fixture-review")
    verify_capsule(c1, trust_code=True)
    original = {
        p.relative_to(c1).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in c1.rglob("*")
        if p.is_file()
    }
    c1_archive = export_capsule(c1, work / "C1.zip")
    research = work / "research-b"
    research.mkdir()
    import_capsule(c1_archive, research / "imported-C1")
    raw_archive = work / "psolver-raw-audit.zip"
    new_memory, results = investigate(
        research / "memory", research / "runtime", raw_archive, backend=backend
    )
    c2 = research / "C2"
    extend_capsule(
        research / "imported-C1",
        LocalFileAdapter(new_memory),
        Goal("Extend to periodic PSolver", ("psolver",)),
        c2,
    )
    verify_capsule(c2, trust_code=True)
    # Curated deterministic fixture review; actual participants review before their own approvals.
    approve_capsule(c2, "deterministic-fixture-review")
    verify_external_artifact(c2, "psolver-raw-audit", raw_archive)
    c2_archive = export_capsule(c2, work / "C2.zip")
    difference = compare_capsules(c1, c2)
    if original != {
        p.relative_to(c1).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in c1.rglob("*")
        if p.is_file()
    }:
        raise RuntimeError("C1 changed during evolution")
    shutil.rmtree(memory.parent)
    shutil.rmtree(new_memory.parent)
    receiver = work / "fresh-receiver"
    receiver.mkdir()
    # Receiving directory is given only C2; no C1 or source-memory file is copied to it.
    transfer = receiver / "transfer.zip"
    shutil.copyfile(c2_archive, transfer)
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in {"PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"}
    }
    process = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(Path(__file__).with_name("receiver.py").resolve()),
            str(transfer),
            str(receiver / "C2"),
            "--backend",
            backend,
        ],
        cwd=receiver,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=180,
    )
    if process.returncode:
        raise RuntimeError("Receiving process failed:\n" + process.stdout + process.stderr)
    continuation = json.loads(process.stdout)
    report = {
        "parent_unchanged": True,
        "source_memories_deleted": True,
        "comparison": difference,
        "sizes": {
            "C1": capsule_size(c1),
            "C2": capsule_size(c2),
            "C1_zip_bytes": c1_archive.stat().st_size,
            "C2_zip_bytes": c2_archive.stat().st_size,
            "raw_audit_zip_bytes": raw_archive.stat().st_size,
        },
        "psolver_results": results,
        "independent_continuation": continuation,
    }
    (work / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--backend", required=True, choices=["docker", "native"])
    args = parser.parse_args()
    print(json.dumps(run(args.output.resolve(), args.backend), indent=2))
