"""Run both sessions; delete source memory before starting the receiving process."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from session_a import generate

from capsule_maker import (
    Goal,
    LocalFileAdapter,
    approve_capsule,
    create_capsule,
    export_capsule,
    verify_capsule,
)


def run(work: Path) -> dict:
    if work.exists():
        raise ValueError("Choose a new output directory")
    work.mkdir(parents=True)
    memory = generate(work / "session-a")
    create_capsule(
        LocalFileAdapter(memory),
        Goal("Continue the numerical convergence study", ("convergence",)),
        work / "capsule-a",
    )
    # This known local fixture is reviewed programmatically by the reproducible demo.
    # General transfers require the researcher's actual content review.
    approve_capsule(work / "capsule-a", "deterministic-demo-fixture-review")
    verify_capsule(work / "capsule-a", trust_code=True)
    archive = export_capsule(work / "capsule-a", work / "poisson.zip")
    shutil.rmtree(work / "session-a")
    shutil.rmtree(work / "capsule-a")
    receiving = work / "session-b"
    receiving.mkdir()
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"}
    }
    capsule = receiving / "capsule"
    subprocess.run(
        [
            sys.executable,
            "-I",
            "-m",
            "capsule_maker.cli",
            "import",
            str(archive),
            str(capsule),
        ],
        cwd=receiving,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            sys.executable,
            "-I",
            "-m",
            "capsule_maker.cli",
            "verify",
            str(capsule),
            "--trust-code",
        ],
        cwd=receiving,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    continued = subprocess.run(
        [sys.executable, "-B", str(capsule / "consumer.py")],
        cwd=capsule,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(continued.stdout)
    result["source_memory_deleted_before_consumer"] = not (work / "session-a").exists()
    (receiving / "continuation.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(run(parser.parse_args().output.resolve()), indent=2))
