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
from .evolution import (
    capsule_identifier,
    capsule_size,
    compare_capsules,
    extend_capsule,
    verify_external_artifact,
    verify_parent,
)

__version__ = "0.1.0a1"
__plugin_version__ = "0.1.0-alpha"
__all__ = [
    "CapsuleError",
    "Goal",
    "LocalFileAdapter",
    "MemoryAdapter",
    "approve_capsule",
    "capsule_identifier",
    "capsule_size",
    "check_environment",
    "compare_capsules",
    "create_capsule",
    "export_capsule",
    "extend_capsule",
    "import_capsule",
    "inspect_capsule",
    "resume_knowledge",
    "retrieve_content",
    "select",
    "verify_capsule",
    "verify_external_artifact",
    "verify_parent",
]
