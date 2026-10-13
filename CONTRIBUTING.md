# Contributing

See [quality requirements](docs/quality.md) and
[documentation maintenance](docs/contributing.md). All contributions should use
pull requests with a clear problem, behavior change, and actual validation results.
Main requires an approving reviewer and successful CI checks; see repository
settings for the active protection rules.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m build
.venv/bin/python -m mkdocs build --strict
```

Test scientific assumptions, tolerances, evidence links, portability, and relevant
failure modes. Update user-facing documentation with behavior changes. Preserve
superseded decisions instead of discarding failed scientific approaches. Never
execute imported capabilities without an explicit trust decision. Include only
material you have the right to redistribute. The project license must be chosen
before accepting external contributions or publishing.
