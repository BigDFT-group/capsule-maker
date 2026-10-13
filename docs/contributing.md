# Maintain the project documentation

The website is generated from Markdown in `docs/`. Contributors update the same
repository as the library; no separate website account or manual HTML editing is
needed. Documentation is hosted on GitHub Pages and deployed through GitHub Actions.

## Build and preview

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-docs.txt
.venv/bin/python -m mkdocs build --strict
.venv/bin/python -m mkdocs serve
```

Follow the local address printed by MkDocs. `site/` contains the generated pages
and is ignored by Git. Edit Markdown, `mkdocs.yml`, or the stylesheet; do not edit
generated HTML.

## Submit an update

Create a branch or fork, make a focused change, and run the strict build. Submit a
pull request describing the reader's need and what changed. Include supporting
sources for factual or scientific claims. A documentation change should distinguish
implemented functionality, proposed behavior, and future work.

Use relative Markdown links between documentation pages. Add new pages to the
navigation in `mkdocs.yml`. Keep executable examples accurate and include their
prerequisites and expected outputs once the implementation exists.

The [quality requirements](quality.md) define the review and merge rules.
The repository pull-request template makes the relevant evidence visible.

## Continuous checks and publication

The `Documentation` workflow runs `mkdocs build --strict` on pull requests
and pushes to main. It checks documentation configuration and internal links.
It does not verify remote URLs or scientific claims. The `Python CI` workflow
checks the Python test suite and packaging; its wheel-installed Poisson handover
exercises the distribution outside the editable development installation.
For implementation changes, install `.[dev]` and run `python -m pytest -q` and
`python -m build` as well as the strict documentation build.

The `Documentation` workflow builds every pull request strictly. On main, it
uploads the checked site as a Pages artifact and deploys through the `github-pages`
environment. Fork pull requests cannot deploy. Edit Markdown and submit a pull
request; do not upload generated HTML manually.

## Reference material and rights

The supplied concept note and *Capsule-Maker and AOM* PDF inform the design but are
not included in the published source pending redistribution permission. Summaries
must avoid overstating the benchmark evidence. The project's license remains a
publication decision; it has not been selected by this draft.
