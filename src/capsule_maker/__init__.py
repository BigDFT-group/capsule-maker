"""Portable Research Memory for Reproducible AI-Assisted Science."""

from .adapters import LocalFileAdapter, MemoryAdapter
from .core import (
    CapsuleError,
    Goal,
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

__version__ = "0.1.0"
__all__ = [
    "CapsuleError",
    "Goal",
    "LocalFileAdapter",
    "MemoryAdapter",
    "approve_capsule",
    "check_environment",
    "create_capsule",
    "export_capsule",
    "import_capsule",
    "inspect_capsule",
    "resume_knowledge",
    "retrieve_content",
    "select",
    "verify_capsule",
]
