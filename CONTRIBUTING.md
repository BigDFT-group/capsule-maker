# Contributing

See [quality requirements](docs/quality.md) and
[documentation maintenance](docs/contributing.md). All contributions should use
pull requests with a clear problem, behavior change, and actual validation results.
Main requires successful CI checks. During the initial single-maintainer phase,
the project owner may review and merge their own PR; independent approval is not
required. See the quality requirements and repository settings for this explicitly
authorized exception and the conditions for restoring independent review.

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
material you have the right to redistribute. Contributions are accepted
under the MIT license in LICENSE; include only compatible redistributable artifacts.
