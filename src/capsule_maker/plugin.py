"""Prepare a workspace-bound local plugin; never modify a harness's user config."""

import json
import re
import shutil
import sys
import tempfile
from importlib import resources
from pathlib import Path

from . import __version__
from .core import CapsuleError, safe_path


def _skill_text() -> str:
    packaged = resources.files("capsule_maker").joinpath("resources/SKILL.md")
    if packaged.is_file():
        return packaged.read_text(encoding="utf-8")
    # Editable development installations use the same canonical Skill source.
    source = Path(__file__).resolve().parents[2] / "skills/capsule-maker/SKILL.md"
    if source.is_file():
        return source.read_text(encoding="utf-8")
    raise CapsuleError("The installed distribution is missing its Agent Skill")


def prepare_local_plugin(workspace: str | Path, marketplace: str) -> dict:
    """Create a local catalog, portable bundle, and Codex compatibility metadata.

    The caller chooses an existing workspace and explicitly installs/enables the
    result in their harness. No model call, dependency installation, registered
    connection, global configuration change, or publication occurs here.
    """
    root = Path(workspace).absolute()
    if root.is_symlink() or not root.is_dir():
        raise CapsuleError("Plugin workspace must be an existing regular directory")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", marketplace):
        raise CapsuleError(
            "Marketplace name must use lowercase letters, digits, and hyphens"
        )
    destination = safe_path(root, "plugins/capsule-maker")
    # .agents is a host convention, not a capsule artifact path.
    catalog_dir = root / ".agents" / "plugins"
    for path in (root / ".agents", catalog_dir):
        if path.is_symlink():
            raise CapsuleError("Symlink configuration directories are not permitted")
    catalog = catalog_dir / "marketplace.json"
    if (
        destination.exists()
        or destination.is_symlink()
        or catalog.exists()
        or catalog.is_symlink()
    ):
        raise CapsuleError(
            "Plugin or marketplace already exists; choose a fresh workspace"
        )
    python = str(
        Path(sys.executable).absolute()
    )  # preserve the virtualenv interpreter symlink
    config = {
        "mcpServers": {
            "capsule-maker": {
                "command": python,
                "args": [
                    "-I",
                    "-m",
                    "capsule_maker.mcp_server",
                    "--workspace",
                    str(root),
                ],
            }
        }
    }
    manifest = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": "capsule-maker",
        "version": __version__,
        "description": "Create and retrieve portable research capsules with evidence and corrections.",
        "author": {"name": "Capsule-Maker contributors"},
        "keywords": ["science", "research", "reproducibility", "memory"],
    }
    compatibility = {
        "name": manifest["name"],
        "version": manifest["version"],
        "description": manifest["description"],
        "skills": "./skills/",
        "mcpServers": "./.mcp.json",
        "interface": {
            "displayName": "Capsule-Maker",
            "shortDescription": "Portable scientific handover",
            "developerName": "Capsule-Maker contributors",
            "category": "Productivity",
            "capabilities": ["Read", "Write"],
            "defaultPrompt": [
                "Create a reviewed research capsule from local memory.",
                "Recover research knowledge from an imported capsule.",
            ],
        },
    }
    portable_mcp = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        "mcpServers": {
            "capsule-maker": {"type": "stdio", **config["mcpServers"]["capsule-maker"]}
        },
    }
    runtime = {
        "python": python,
        "workspace": str(root),
        "marketplace": marketplace,
        "plugin": f"capsule-maker@{marketplace}",
        "version": __version__,
    }
    catalog_data = {
        "name": marketplace,
        "interface": {"displayName": marketplace},
        "plugins": [
            {
                "name": "capsule-maker",
                "source": {"source": "local", "path": "./plugins/capsule-maker"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }
        ],
    }
    files = {
        "plugin.json": manifest,
        ".codex-plugin/plugin.json": compatibility,
        "mcp.json": portable_mcp,
        ".mcp.json": config,
        "runtime.json": runtime,
    }
    with tempfile.TemporaryDirectory(prefix="capsule-plugin-", dir=root) as temp:
        stage = Path(temp) / "bundle"
        stage.mkdir()
        for name, data in files.items():
            path = stage / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        skill = stage / "skills/capsule-maker/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(_skill_text(), encoding="utf-8")
        destination.parent.mkdir(parents=True, exist_ok=True)
        stage.rename(destination)
        try:
            catalog_dir.mkdir(parents=True, exist_ok=True)
            with catalog.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(catalog_data, indent=2) + "\n")
        except OSError:
            shutil.rmtree(destination)
            raise
    return {
        **runtime,
        "bundle": str(destination),
        "catalog": str(catalog),
        "installation": "prepared; not installed in the harness",
    }
