"""Local plugin wiring must work after copying into a harness cache."""

import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from capsule_maker import CapsuleError
from capsule_maker.plugin import prepare_local_plugin


def test_plugin_wiring_and_cached_server(memory, tmp_path):
    result = prepare_local_plugin(tmp_path, "capsule-test")
    catalog = json.loads(Path(result["catalog"]).read_text())
    assert catalog["plugins"][0]["source"]["path"] == "./plugins/capsule-maker"
    bundle = Path(result["bundle"])
    assert json.loads((bundle / "plugin.json").read_text())["name"] == "capsule-maker"
    assert (
        "Read"
        in json.loads((bundle / ".codex-plugin/plugin.json").read_text())["interface"][
            "capabilities"
        ]
    )
    assert (bundle / "skills/capsule-maker/SKILL.md").is_file()
    assert not list(bundle.rglob("memory.json"))
    assert not list(bundle.rglob("solver.py"))
    # Host cache relocation must preserve the explicit receiving workspace binding.
    cache = tmp_path / "host-cache"
    shutil.copytree(bundle, cache)
    server = json.loads((cache / ".mcp.json").read_text())["mcpServers"][
        "capsule-maker"
    ]
    assert server["command"] == sys.executable
    assert server["args"][-1] == str(tmp_path)
    portable = json.loads((cache / "mcp.json").read_text())["mcpServers"][
        "capsule-maker"
    ]
    assert portable["type"] == "stdio"

    async def scenario():
        params = StdioServerParameters(
            command=server["command"], args=server["args"], cwd=cache
        )
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                result = await client.call_tool(
                    "create_research_capsule",
                    {
                        "memory": "source/memory.json",
                        "destination": "draft",
                        "objective": "Continue convergence",
                        "tags": ["convergence"],
                    },
                )
                assert not result.isError
                assert (tmp_path / "draft/manifest.json").exists()
                assert not (cache / "draft").exists()

    asyncio.run(scenario())


def test_prepare_plugin_cli(tmp_path):
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "capsule_maker.cli",
            "prepare-plugin",
            "--workspace",
            str(tmp_path),
            "--marketplace",
            "capsule-test",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)["installation"].startswith("prepared")


def test_existing_catalog_preserved(tmp_path):
    existing = tmp_path / ".agents/plugins/marketplace.json"
    existing.parent.mkdir(parents=True)
    existing.write_text('{"name":"existing-team-catalog"}')
    before = existing.read_bytes()
    with pytest.raises(CapsuleError, match="already exists"):
        prepare_local_plugin(tmp_path, "capsule-test")
    assert existing.read_bytes() == before
    assert not (tmp_path / "plugins/capsule-maker").exists()


@pytest.mark.parametrize(
    "marketplace", ["../escape", 'bad"config', "", "Uppercase", "a/b"]
)
def test_invalid_marketplace(tmp_path, marketplace):
    with pytest.raises(CapsuleError, match="Marketplace name"):
        prepare_local_plugin(tmp_path, marketplace)


def test_plugin_config_symlink_rejected(tmp_path):
    root = tmp_path / "workspace"
    root.mkdir()
    (root / ".agents").symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(CapsuleError, match="Symlink"):
        prepare_local_plugin(root, "capsule-test")
