import importlib.util
import sys
from pathlib import Path

import pytest

from capsule_maker import Goal, LocalFileAdapter, create_capsule

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "session_a", ROOT / "examples/poisson/session_a.py"
)
session_a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_a)
sys.modules["session_a"] = session_a


@pytest.fixture
def memory(tmp_path):
    return session_a.generate(tmp_path / "source")


@pytest.fixture
def capsule(memory, tmp_path):
    root = tmp_path / "capsule"
    create_capsule(
        LocalFileAdapter(memory), Goal("Continue convergence", ("convergence",)), root
    )
    return root
