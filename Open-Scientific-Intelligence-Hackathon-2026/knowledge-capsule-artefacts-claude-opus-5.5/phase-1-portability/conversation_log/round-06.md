# Round 06

## Prompt

do you have any HPC plugins, bigdft skills or any relative things?

## Output

Yes. There is a BigDFT plugin installed on this machine, but it's switched off, so its skills aren't loaded in this session.

### What's installed (user scope, `~/.claude/plugins`)
| Plugin | Version | State | Contents |
|---|---|---|---|
| `bigdft@bigdft-skills` (William Dawson) | 0.12.1 | **disabled** (`enabledPlugins: false` in `~/.claude/settings.json`) | 14 skills |
| `ponytail@ponytail` | 5.2.0 | disabled | a "simplest solution" coding style with hooks; not related to HPC or BigDFT |

### The BigDFT plugin's skills
- **For running calculations:**
  - `input`: writing input files
  - `pseudopotentials`: setting pseudopotentials
  - `logfile`: parsing output logs
  - `systems`: building atomic structures
  - `install`: building BigDFT from source
  - `linear-scaling`: setting up linear-scaling runs
- **For HPC (remote clusters):**
  - `remote`: SSH setup, Slurm templates and connection tests for PyBigDFT's RemoteManager
  - `dataset`: submitting batches of runs remotely and chaining them
- **For developers (Fortran):** `futile`, `atlab`, `liborbs`, `projectors`, `psolver` and `variables`.

### What I'm using instead
- **No HPC connector:** no MCP server or plugin for HPC is active. I'm submitting the NLCC jobs directly to the local Slurm node.
- **No Capsule-Maker MCP server:** it isn't installed either (see round 02).
- **Local BigDFT install:** five 1.9.5 builds sit in `~/Softwares`. I'm using the plain `bigdft` build for the NLCC runs.

### Checking the running jobs against the `pseudopotentials` skill
The skill recommends `inp.set_psp_nlcc(elements=['C', 'H', 'O', 'N'])`. I tested that call in our PyBigDFT 1.9.6:
- With a list of elements, it loads **nothing** (0 pseudopotential entries). This is the same bug C1 recorded as `fail-psp-api`.
- With no arguments, it loads all 31 NLCC elements.

So the skill's example doesn't work with this PyBigDFT version. The running inputs don't use that call: they load each file explicitly, C1's Krack files first and then the NLCC files on top. I checked the generated inputs: C, H and O are NLCC, S is C1's Krack file, and there are 72 electrons. The running jobs are not affected.

If you want, I can switch the BigDFT plugin on (`/plugin`, or set `enabledPlugins` to `true`). Its skills would then load from the next session onward.

## Time and tokens

| Metric | Value |
|---|---|
| Prompt sent (UTC) | 2026-10-21 08:46:33 |
| Last reply (UTC) | 2026-10-21 08:47:25 |
| Wall time | 0 min 52 s |
| API requests | 7 |
| Input tokens (uncached) | 14 |
| Cache-write input tokens | 10,321 |
| Cache-read input tokens | 1,010,402 |
| Output tokens | 5,595 |
| Total tokens | 1,026,332 |

_Source: session transcript, computed by `round_stats.py`. Does not include the compute time of background jobs._
