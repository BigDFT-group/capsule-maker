"""Normalized backend contract. This module never calls a memory service."""

from abc import ABC, abstractmethod
from pathlib import Path


class MemoryAdapter(ABC):
    """Supply a JSON-compatible snapshot and UTF-8 artifact bytes.

    snapshot() follows memory-v1.schema.json. read_artifact() accepts only a path
    declared by the snapshot. Backends retain responsibility for consolidation.
    """

    @abstractmethod
    def snapshot(self) -> dict:
        """Return records, sources, artifact descriptions, and origin."""

    @abstractmethod
    def read_artifact(self, path: str) -> bytes:
        """Return one declared artifact; do not execute it."""


class LocalFileAdapter(MemoryAdapter):
    """Read a normalized JSON memory file and artifacts relative to that file."""

    def __init__(self, memory_file: str | Path):
        self.memory_file = Path(memory_file).absolute()

    def snapshot(self) -> dict:
        from .core import read_json

        return read_json(self.memory_file)

    def read_artifact(self, path: str) -> bytes:
        from .core import CapsuleError, read_bytes, safe_path

        target = safe_path(self.memory_file.parent, path)
        if path not in {item["path"] for item in self.snapshot()["artifacts"]}:
            raise CapsuleError("Artifact is not declared by the adapter snapshot")
        return read_bytes(target)
