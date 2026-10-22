"""Per-round time and token usage from a Claude Code session transcript; writes it into round-NN.md.

    python3 -I conversation_log/round_stats.py SESSION.jsonl conversation_log

A round starts at a user prompt typed by the user and ends at the last assistant message before the next prompt.
Tokens are summed once per API request (the transcript repeats usage for every content block of a message).
Background work that outlives a round (e.g. Slurm jobs) is not counted; wake-ups it triggers count in the round
during which they arrive.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SESSION, LOGDIR = Path(sys.argv[1]), Path(sys.argv[2])
HEAD = "## Time and tokens"


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def is_prompt(d):
    if d.get("type") != "user" or d.get("isMeta"):
        return False
    c = d["message"]["content"]
    if not isinstance(c, str):
        return False
    return not c.lstrip().startswith(("<local-command", "<command-name>", "<task-notification", "<system-reminder"))


rounds, seen = [], set()
for line in SESSION.read_text().splitlines():
    d = json.loads(line)
    if is_prompt(d):
        rounds.append(dict(start=ts(d["timestamp"]), end=ts(d["timestamp"]), requests=0,
                           input=0, cache_write=0, cache_read=0, output=0))
    elif d.get("type") == "assistant" and rounds:
        r = rounds[-1]
        r["end"] = max(r["end"], ts(d["timestamp"]))
        key = d.get("requestId") or d["message"].get("id")
        u = d["message"].get("usage")
        if u and key not in seen:
            seen.add(key)
            r["requests"] += 1
            r["input"] += u.get("input_tokens", 0)
            r["cache_write"] += u.get("cache_creation_input_tokens", 0)
            r["cache_read"] += u.get("cache_read_input_tokens", 0)
            r["output"] += u.get("output_tokens", 0)

for i, r in enumerate(rounds, 1):
    md = LOGDIR / f"round-{i:02d}.md"
    if not md.exists():
        continue
    secs = int((r["end"] - r["start"]).total_seconds())
    total = r["input"] + r["cache_write"] + r["cache_read"] + r["output"]
    block = (f"{HEAD}\n\n"
             f"| Metric | Value |\n|---|---|\n"
             f"| Prompt sent (UTC) | {r['start']:%Y-%m-%d %H:%M:%S} |\n"
             f"| Last reply (UTC) | {r['end']:%Y-%m-%d %H:%M:%S} |\n"
             f"| Wall time | {secs // 60} min {secs % 60:02d} s |\n"
             f"| API requests | {r['requests']} |\n"
             f"| Input tokens (uncached) | {r['input']:,} |\n"
             f"| Cache-write input tokens | {r['cache_write']:,} |\n"
             f"| Cache-read input tokens | {r['cache_read']:,} |\n"
             f"| Output tokens | {r['output']:,} |\n"
             f"| Total tokens | {total:,} |\n\n"
             f"_Source: session transcript, computed by `round_stats.py`. Does not include the "
             f"compute time of background jobs._\n")
    text = md.read_text()
    text = re.sub(rf"\n{HEAD}\n.*", "", text, flags=re.S).rstrip("\n") + "\n\n" + block
    md.write_text(text)
    print(f"round {i:02d}: {secs // 60}m{secs % 60:02d}s, {r['requests']} requests, {total:,} tokens "
          f"(out {r['output']:,})")
