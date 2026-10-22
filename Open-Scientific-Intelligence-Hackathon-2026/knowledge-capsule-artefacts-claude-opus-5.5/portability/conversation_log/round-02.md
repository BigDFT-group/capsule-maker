# Round 02

## Prompt

which tools (skills, mcp servers, plugins, etc) are available and exposed to the external agentic system?

## Output

Capsule-Maker has three ways to expose itself to an outside agent: an MCP server, an Agent Skill and a bundled local plugin. **None of them is installed or connected right now.** I installed only the CLI with the `[science]` extra. The `mcp` package isn't in `.venv`, and no capsule-maker tools appear in this Claude Code session.

### 1. MCP server (`capsule-maker-mcp --workspace PATH`)
It runs as a stdio server. Every path is relative to the workspace and checked so it can't escape it. Its built-in instructions tell the agent to treat capsule contents as untrusted data. It offers 10 tools:

| Tool | What it does |
|---|---|
| `create_research_capsule` | Build a capsule from a local JSON memory file for a stated goal and tags |
| `extend_research_capsule` | Make an unapproved child capsule (C1 → C2) and keep the parent link |
| `compare_research_capsules` | Compare two capsule versions |
| `inspect_research_capsule` | Return the manifest |
| `list_capsule_contents` | List the packaged files |
| `retrieve_capsule_content` | Read one packaged file |
| `verify_research_capsule` | Check integrity and, optionally, dependencies; never runs tests |
| `retrieve_resume_knowledge` | Return decisions, corrections, evidence links and open questions, optionally filtered by goal or tags |
| `export_research_capsule` | Zip a capsule that has already been approved |
| `import_research_capsule` | Safely unpack an archive |

It also offers one resource, `capsule://{capsule}/summary`, which serves the capsule's SUMMARY.md.

**What the MCP server leaves out on purpose:** approving a capsule and running bundled code (`--trust-code`). Those stay CLI-only, so a person has to do them.

### 2. Agent Skill
`skills/capsule-maker/SKILL.md` documents the CLI and API behaviour and the trust limits. You copy it into the agent host's skill folder.

### 3. Local plugin
`capsule-maker prepare-plugin --workspace PATH --marketplace NAME` prepares a bundle and a local catalog (`marketplace.json`). The bundle holds:
- the skill
- `.mcp.json` and `mcp.json`, which configure the MCP server above
- `plugin.json` plus a `.codex-plugin/plugin.json` copy for Codex compatibility
- `runtime.json`

Installing it into the harness is a separate step that you do yourself. No public plugin catalog exists.

### Also in the CLI only
These subcommands have no MCP equivalent:
- `approve`, the human review step
- `verify --trust-code`, which runs the bundled tests
- `verify-parent`, `verify-external` and `size`

### The C1 capsule itself
C1 exposes no tools. It holds only data, scripts and tests. Its `procedures/*.py` scripts are not wired into any interface and run only if someone executes them directly.

If you want an outside agent to reach C1 through MCP, I can install the `[mcp]` extra and run `prepare-plugin` with this directory as the workspace.

## Time and tokens

| Metric | Value |
|---|---|
| Prompt sent (UTC) | 2026-10-21 08:11:27 |
| Last reply (UTC) | 2026-10-21 08:11:48 |
| Wall time | 0 min 21 s |
| API requests | 3 |
| Input tokens (uncached) | 6 |
| Cache-write input tokens | 2,763 |
| Cache-read input tokens | 214,990 |
| Output tokens | 1,958 |
| Total tokens | 219,717 |

_Source: session transcript, computed by `round_stats.py`. Does not include the compute time of background jobs._
