# Quick start: create a capsule with your agent

Use one model to create a capsule, then another model in a fresh conversation to
[retrieve and continue it](quickstart-retrieve.md). This page supplies copy-paste
prompts and a local plugin installation path. The tutorial creates local research artifacts; it does not upload your research.

The first exercise uses an actually computed, structured Poisson investigation.
The creator model selects and assembles the handover; it does not discover the
science from scratch. Conversation consolidation remains the memory backend's
responsibility. This first trial measures plugin usability and research transfer.

## Get the installation source

Clone the tagged release in a terminal, outside the receiving conversation:

```bash
git clone --branch v0.1.0-alpha https://github.com/BigDFT-group/capsule-maker.git
cd capsule-maker
```

Use this checkout only for installation. The model's conversation will run in its
separate workspace; do not give the receiving model the repository examples or
creator notes as research inputs.

## 1. Install the local plugin

Prerequisites: a reviewed local Capsule-Maker checkout, Python 3.11+, and a coding
harness with shell access and local stdio MCP support. The commands below target
Codex CLI; they were checked against CLI 0.159.3. For the desktop app, use its local
Plugins Directory and open the same workspace after installation. Ordinary web-only
chat cannot launch this local server without an additional connection mechanism.

From the Capsule-Maker checkout, run in a terminal:

```bash
CAPSULE_SOURCE="$PWD"
CAPSULE_AUTHOR="/tmp/capsule-author"
python3 -m venv "$CAPSULE_AUTHOR/.venv"
"$CAPSULE_AUTHOR/.venv/bin/python" -m pip install "${CAPSULE_SOURCE}[science,mcp]"
"$CAPSULE_AUTHOR/.venv/bin/python" -m capsule_maker.cli prepare-plugin \
  --workspace "$CAPSULE_AUTHOR" --marketplace capsule-author
codex plugin marketplace add "$CAPSULE_AUTHOR"
codex plugin add capsule-maker@capsule-author
```

Choose a fresh directory. `prepare-plugin` creates a portable manifest, Codex
compatibility manifest, MCP connection, Skill, and local marketplace catalog.
It preserves existing catalogs by refusing to overwrite them. It does not install
into your harness or change global settings; the two `codex plugin` commands perform
that installation explicitly. No memory credentials or paid API key are needed by
Capsule-Maker itself; your harness's model usage follows its normal account terms.

The bundle lives under `plugins/capsule-maker/`; `runtime.json` records its Python
interpreter and workspace. Keep that virtual environment and workspace in place
while the plugin is installed. A cached plugin continues to use those absolute
paths. Do not copy the author's configured bundle to the receiving workspace;
prepare a separate receiving bundle instead.

The installation flow follows the [official plugin packaging guidance](https://developers.openai.com/plugins/build/plugins).
If your CLI has different subcommands, check `codex plugin --help` and use the
supported local Plugins Directory. If your harness supports MCP and Skills but
not this plugin format, connect the generated `.mcp.json` and Skill through its
supported configuration; record the trial as manual integration, not plugin installation.

## 2. Prepare the scientific source

In the same terminal:

```bash
"$CAPSULE_AUTHOR/.venv/bin/python" -B \
  "$CAPSULE_SOURCE/examples/poisson/session_a.py" "$CAPSULE_AUTHOR/source"
codex -C "$CAPSULE_AUTHOR"
```

Select your creator model through the harness's model selector. Enable only the
`capsule-maker@capsule-author` instance for this conversation. Start a new
conversation rather than resuming this project's development chat.

The generator calculates numerical evidence and creates `source/memory.json` plus
its supporting files. It includes an incorrect sign choice, its correction, a
validated solver, regression tests, an unresolved next calculation, and unrelated
records. It runs known locally authored example code; it does not execute an
imported capsule. Source generation happens before the model's handover task.

## 3. Copy and paste the creation prompt

Paste this whole block into the fresh creator conversation:

```text
Use the installed Capsule-Maker plugin for this workspace.

First check the plugin's runtime.json and identify the configured workspace and
Python interpreter. Confirm that the Capsule-Maker MCP tools are available.
If the plugin is missing, ambiguous, or points at another workspace, stop and
report the setup problem; do not silently replace the plugin with an improvised
implementation.

The existing source/memory.json is a curated scientific investigation. Read its
records and supporting numerical evidence. Do not claim that you generated or
consolidated this investigation from our conversation.

Create a capsule in draft for this objective:
"Continue the numerical convergence study, carrying the validated solver,
rejected approaches, scientific decisions, supporting evidence, regression
tests, and unresolved next calculation."

Use the plugin's create, inspect, and content-retrieval tools. Determine suitable
selection tags from the actual source metadata. Preserve corrections and
superseded decisions, and exclude unrelated research. Do not change scientific
records or invent missing evidence just to make creation succeed.

Show me the review summary, included and excluded record IDs with reasons,
correction links, evidence/provenance, packaged files, dependencies, and any
reported contradictions. Distinguish verified, hypothetical, and unresolved
knowledge. Save your explanation as creation-report.md outside draft.

Do not approve or export yet, and do not execute bundled Python. Stop with a
concrete capsule ready for my review. Report actual tool failures honestly.
```

If your harness requires selecting a plugin explicitly, select Capsule-Maker in
its picker before sending the prompt. Tool namespaces may vary by host; the tool
operations are those described in [interfaces](interfaces.md).

## 4. Review, authorize validation, and export

Read the actual summary, source references, numerical evidence, solver, consumer,
and tests. Check that sensitive or unlicensed information is absent. Approval is
a recorded review decision, not an authenticated signature.

Only once you have completed that review, paste:

```text
I have reviewed the capsule in draft and approve this content for transfer.
Record my approval with reviewer ID quick-start-owner using Capsule-Maker's
CLI/API and the Python interpreter declared by this plugin.

I explicitly trust the locally supplied example code in this reviewed capsule.
Run its bundled regression tests through Capsule-Maker's trusted validation
operation. Do not weaken tolerances or alter the capsule if tests fail.

If approval, integrity checks, dependencies, and regression tests pass, use the
plugin's export tool to create handover.zip in this workspace. Compute and report
its SHA-256 digest. Update creation-report.md with the actual validation results
and archive digest, keeping the report outside the capsule. Do not publish or
send the archive anywhere.
```

MCP deliberately exposes no approval or execution tool, so those two operations
use the declared CLI/API. Trusted tests run with your OS privileges, not inside a
security sandbox. Read [security](security.md) before authorizing third-party code.

You should now have `handover.zip` and `creation-report.md`. Do not assume export
worked unless the file exists and the reported validation completed.

## 5. Transfer only the capsule

Give the receiving session **only `handover.zip`**, plus the plugin/runtime setup.
Do not provide the source memory, creation report, original conversation, this
page, or expected scientific answers. Use the [retrieval quick start](quickstart-retrieve.md).
For multiple receiver models, preserve this exact archive and its SHA-256 digest.

## Creator checklist (keep out of the receiving prompt)

For the supplied fixture, selection should include `validated-solver`, `problem`,
`boundary-decision`, `correct-sign`, `wrong-sign`, `numerical-evidence`, and
`next-grid`, while excluding `unrelated` and `generalization`. The correction must
retain the superseded failed choice and the evidence must point to `results.json`.
The portable regression suite contains four tests. The intended continuation is
at a new resolution; its criteria and expected numerical scale are documented in
the [scientific demonstration](demonstration.md).

This checklist supports review; it is not evidence that a model recovered the
knowledge. Save the actual creator conversation and tool-call trace separately,
with the selected model, reasoning setting if available, harness version, plugin
version, and any manual intervention. Never include credentials in those logs.
