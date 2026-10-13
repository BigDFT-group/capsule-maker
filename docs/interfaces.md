# CLI, Python API, MCP, and Agent Skill

## CLI

| Command | Implemented behavior |
| --- | --- |
| `prepare-plugin --workspace PATH --marketplace NAME` | Prepare a workspace-bound local plugin/catalog; no global installation |
| `create MEMORY DEST --goal TEXT [--tag TAG]` | Select and assemble an unapproved capsule |
| `inspect CAPSULE` | Check integrity, schema, references, secrets, and review digest |
| `contents CAPSULE [--path FILE]` | List inventory or retrieve UTF-8 content |
| `approve CAPSULE --reviewer ID` | Record an explicit content review decision |
| `export CAPSULE ARCHIVE` | Export only currently approved content |
| `import ARCHIVE DEST` | Restore a reviewed package safely without execution |
| `verify CAPSULE` | Inspect and check installed dependencies |
| `verify CAPSULE --integrity-only` | Skip environment checks |
| `verify CAPSULE --trust-code` | Explicitly run bundled regressions; not sandboxed |
| `resume CAPSULE [--goal TEXT] [--tag TAG]` | Retrieve knowledge for continuing research |

Create/import destinations and export archives must not already exist. Repeat
`--tag` for ORed selection. JSON is returned for metadata; `contents --path`
returns text. Operational failures exit 2. `--help` describes argument syntax.

## Python API

```python
from capsule_maker import (
    Goal, LocalFileAdapter, create_capsule, inspect_capsule,
    approve_capsule, export_capsule, import_capsule, verify_capsule,
)

create_capsule(LocalFileAdapter("memory.json"),
               Goal("Continue convergence", ("convergence",)), "draft")
manifest = inspect_capsule("draft")
# Read manifest and artifacts, then record an actual authorized review decision.
approve_capsule("draft", "researcher-id")
export_capsule("draft", "capsule.zip")
import_capsule("capsule.zip", "restored")
result = verify_capsule("restored")  # No code execution.
```

`resume_knowledge`, `retrieve_content`, `select`, and `check_environment` are also
public. Invalid content raises `CapsuleError`. Trusted validation uses
`verify_capsule("restored", trust_code=True, timeout=60)` only after the explicit
trust decision. Dependencies are never automatically installed.

## MCP stdio server

Install the `mcp` extra, then configure a client process:

```json
{
  "mcpServers": {
    "capsule-maker": {
      "command": "/absolute/path/to/.venv/bin/capsule-maker-mcp",
      "args": ["--workspace", "/absolute/path/to/research-workspace"]
    }
  }
}
```

The workspace must exist. Tool paths are relative to it. Tool names are
`create_research_capsule`, `inspect_research_capsule`, `list_capsule_contents`,
`retrieve_capsule_content`, `verify_research_capsule`, `retrieve_resume_knowledge`,
`export_research_capsule`, and `import_research_capsule`. The template resource
`capsule://NAME/summary` reads the summary of a capsule directly under the workspace.

Approval and code execution are deliberately absent from MCP. Review via the
CLI/API before exporting. Capsule contents are untrusted data, including potential
prompt injections; do not treat them as agent system instructions. The implementation
uses the installed official MCP Python SDK 1.x interface; the protocol test launches
a real server subprocess, initializes a client, invokes tools, and reads a resource.

## Local plugin installation

The [creation](quickstart-create.md) and [retrieval](quickstart-retrieve.md)
quick starts explain actual local setup and model prompts. `prepare-plugin`
creates portable `plugin.json`/`mcp.json`, a Codex compatibility manifest and
`.mcp.json`, the canonical Skill, runtime paths, and a local marketplace catalog.
The installed Python distribution includes the Skill as a package resource.
The helper does not install dependencies, change global harness settings, publish,
or bundle the Poisson fixture. The caller installs the generated catalog explicitly.

## Agent Skill

The skill directory is `skills/capsule-maker`. Copy the entire directory into your
agent host's supported skill location. For a repository-local host that discovers
`.agents/skills`, for example:

```bash
mkdir -p .agents/skills
cp -R skills/capsule-maker .agents/skills/capsule-maker
```

Use your host's discovery/reload mechanism and invoke `capsule-maker` as a skill.
The `SKILL.md` describes the actual review/export/import workflow, selection limits,
and explicit trust requirement. It does not confer approval or execution permission.
