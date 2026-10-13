"""Exercise the actual MCP stdio transport with an independent server process."""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from capsule_maker import approve_capsule


def text_result(result):
    assert not result.isError, result.content
    return "\n".join(item.text for item in result.content if item.type == "text")


def test_mcp_protocol(memory, tmp_path):
    async def scenario():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-I", "-m", "capsule_maker.mcp_server", "--workspace", str(tmp_path)],
        )
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                tools = (await client.list_tools()).tools
                names = {tool.name for tool in tools}
                assert {
                    "create_research_capsule",
                    "inspect_research_capsule",
                    "verify_research_capsule",
                    "retrieve_resume_knowledge",
                    "retrieve_capsule_content",
                } <= names
                assert not any(
                    "trust_code" in tool.inputSchema.get("properties", {})
                    for tool in tools
                )
                created = await client.call_tool(
                    "create_research_capsule",
                    {
                        "memory": "source/memory.json",
                        "destination": "capsule",
                        "objective": "Continue convergence",
                        "tags": ["convergence"],
                    },
                )
                assert "correct-sign" in text_result(created)
                inspected = await client.call_tool(
                    "inspect_research_capsule", {"capsule": "capsule"}
                )
                assert "numerical-evidence" in text_result(inspected)
                listed = await client.call_tool(
                    "list_capsule_contents", {"capsule": "capsule"}
                )
                assert "solver.py" in text_result(listed)
                content = await client.call_tool(
                    "retrieve_capsule_content",
                    {"capsule": "capsule", "content_path": "SUMMARY.md"},
                )
                assert "Research Capsule" in text_result(content)
                verified = await client.call_tool(
                    "verify_research_capsule", {"capsule": "capsule"}
                )
                assert "not run" in text_result(verified)
                resumed = await client.call_tool(
                    "retrieve_resume_knowledge", {"capsule": "capsule"}
                )
                assert "wrong-sign" in text_result(resumed)
                resource = await client.read_resource("capsule://capsule/summary")
                assert "Research Capsule" in resource.contents[0].text
                blocked = await client.call_tool(
                    "export_research_capsule",
                    {"capsule": "capsule", "archive": "capsule.zip"},
                )
                assert blocked.isError
                approve_capsule(tmp_path / "capsule", "mcp-test-reviewer")
                exported = await client.call_tool(
                    "export_research_capsule",
                    {"capsule": "capsule", "archive": "capsule.zip"},
                )
                assert "capsule.zip" in text_result(exported)
                imported = await client.call_tool(
                    "import_research_capsule",
                    {"archive": "capsule.zip", "destination": "restored"},
                )
                assert "correct-sign" in text_result(imported)
                escaped = await client.call_tool(
                    "inspect_research_capsule", {"capsule": "../outside"}
                )
                assert escaped.isError
                (tmp_path / "outside-link").symlink_to(
                    tmp_path.parent, target_is_directory=True
                )
                linked = await client.call_tool(
                    "inspect_research_capsule", {"capsule": "outside-link/capsule"}
                )
                assert linked.isError

    asyncio.run(scenario())
