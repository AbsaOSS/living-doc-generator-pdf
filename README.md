# Living Doc Generator PDF

[![Build and Test](https://github.com/AbsaOSS/living-doc-generator-pdf/actions/workflows/test.yml/badge.svg)](https://github.com/AbsaOSS/living-doc-generator-pdf/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A source-agnostic GitHub Action that renders **any** structured JSON into a professional PDF using Jinja2 templates and WeasyPrint. It ships with three built-in document types and supports fully custom template packs.

## Overview

> **Expected usage: GitHub Actions first.** The supported way to run this action is as a step in a GitHub Actions workflow, chained with the other `living-doc-*` actions. Running it locally — the `run_script.sh` / `python3 main.py` pattern documented in `DEVELOPER.md` — is a development and debugging affordance only, not a second supported deployment target.

> **The Living Documentation pipeline runs AI-free.** Every step — collect → normalize → generate — is deterministic tooling (Python, JSON Schema validation, Jinja2/Markdown templates) with no LLM call anywhere in that path. [`AbsaOSS/agentic-toolkit`](https://github.com/AbsaOSS/agentic-toolkit) can accelerate the upstream *authoring* of GitHub Issues and `.feature` files, but it is never a runtime dependency of this pipeline: a human writing the same input by hand is a fully supported, identical path.

The action is a generic JSON-to-PDF engine: you provide a JSON source file and either a built-in `document-type` or your own `template-path`. The raw JSON is passed to the templates unchanged as `data`, alongside injected `meta` (title, timestamp, source file name).

**Built-in document types**

| `document-type` | Purpose | Typical source |
|-----------------|---------|----------------|
| `technical-project` | User stories, features, and acceptance criteria | `generator-ready.json` |
| `ui-test-catalog` | BDD/UI test scenarios grouped by feature file | `ui-tests.json` |
| `coverage-matrix` | AC-to-test coverage report | `coverage-matrix.json` |

`generator-ready.json` is **not** raw collector output — it is the normalized,
schema-versioned artifact produced by the toolkit's `normalize-issues` step. See
[Producing `generator-ready.json`](#producing-generator-readyjson) for the
end-to-end `collector → toolkit normalize → generator-pdf` workflow.

**Key features**
- 📄 Source-independent: renders raw JSON; no knowledge of GitHub, Jira, etc.
- 🎨 Template-driven: built-in sets plus full or partial custom overrides
- ✅ Validated by default: every built-in `document-type` is checked against its
  own vendored schema with no configuration
- ⚡ Deterministic: same input always produces the same output
- 🔍 Debug mode: save the intermediate HTML for troubleshooting
- 📊 Reporting: emits `pdf_report.json` with statistics

## Usage

### Prerequisites

- **Python 3.10 or later.**
- **System dependencies** (WeasyPrint): `libpango-1.0-0`, `libpangocairo-1.0-0`, `libgdk-pixbuf2.0-0`, `libffi-dev`, `libcairo2`. These are installed automatically by the action on Ubuntu runners.

### Adding the Action to Your Workflow

This action is the **last** step of the Living Documentation pipeline. It consumes
`generator-ready.json`, which is produced by the toolkit's `normalize-issues` step —
never by feeding raw collector output straight into this action.

```yaml
- name: Generate PDF
  uses: AbsaOSS/living-doc-generator-pdf@v1
  with:
    # generator-ready.json comes from `living-doc normalize-issues` (see below)
    source-path: 'generator-ready.json'
    document-type: 'technical-project'
    output-path: 'documentation.pdf'
```

#### Producing `generator-ready.json`

The recommended, supported path is `collector → toolkit normalize → generator-pdf`.
The collector mines the source system, the toolkit's `normalize-issues` service
converts that raw output into the canonical, schema-versioned `generator-ready.json`
envelope (`meta` + `content`, `schema_version: "generator-ready-v1.0.0"`), and this
action renders it:

```yaml
# .github/workflows/generate-docs.yml
name: Generate Documentation PDF

on:
  push:
    branches: [main]

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Collect issues
        uses: AbsaOSS/living-doc-collector-gh@v0.1.0
        with:
          doc-issues: 'true'
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # see the collector README for mode-specific inputs

      - uses: actions/upload-artifact@v4
        with:
          name: collector-output
          path: output/

  normalize:
    needs: collect
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: collector-output
          path: output/

      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install the toolkit
        run: pip install living-doc-toolkit

      - name: Normalize collector output to generator-ready.json
        run: |
          living-doc normalize-issues \
            --input output/doc-issues.json \
            --output generator-ready.json \
            --source collector-gh \
            --document-title 'Product Backlog'

      - uses: actions/upload-artifact@v4
        with:
          name: generator-ready
          path: generator-ready.json

  generate-pdf:
    needs: normalize
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: generator-ready

      - name: Generate PDF
        uses: AbsaOSS/living-doc-generator-pdf@v1
        with:
          source-path: 'generator-ready.json'
          document-type: 'technical-project'
          output-path: 'documentation.pdf'
          document-title: 'Product Backlog'
          debug-html: 'true'
          verbose: 'true'

      - name: Upload PDF
        uses: actions/upload-artifact@v4
        with:
          name: documentation-pdf
          path: documentation.pdf
```

> The exact collector inputs and the toolkit install command depend on your source
> system and release; treat the step bodies above as a shape, and follow
> [the toolkit's `normalize-issues` cookbook][toolkit-normalize] and
> [its GitHub Actions recipe][toolkit-recipe] for the authoritative commands.

[toolkit-normalize]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/cookbooks/normalize-issues.md
[toolkit-recipe]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/recipes/github-actions-normalize-issues.md
[ecosystem-dataflow]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/architecture.md

For how `generator-ready.json` fits the wider ecosystem contract, see the
[Living Documentation data-flow architecture][ecosystem-dataflow].

## Action Configuration

### Environment Variables

None. All configuration is passed through the `with:` inputs below.

### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source-path` | string (path) | **Yes** | - | Path to the source JSON file to render |
| `document-type` | string | Conditional | - | Built-in set: `technical-project`, `ui-test-catalog`, or `coverage-matrix` |
| `template-path` | string (path) | Conditional | - | Custom template directory (overrides or extends a built-in set) |
| `output-path` | string (path) | No | `output.pdf` | Path for the generated PDF |
| `document-title` | string | No | _(derived)_ | Cover-page title |
| `schema-path` | string (path) | No | - | **Advanced / bring-your-own.** Overrides the default validation with a custom JSON Schema. Unsupported — the recommended path is to feed a normalized `generator-ready.json` and let default validation run. |
| `debug-html` | boolean | No | `false` | Save the rendered HTML next to the PDF |
| `verbose` | boolean | No | `false` | Enable verbose logging |
| `pdf_ready_json` | string (path) | No | - | **Deprecated** alias for `source-path` |

At least one of `document-type` or `template-path` must be provided. When `document-title` is not set, the title is derived from the document type's default (e.g. "Technical Project") or the source file name.

Every built-in `document-type` is **validated by default**: when no `schema-path` is given, the source is checked against the vendored schema for that type — `generator-ready-v1.0.0-schema.json` for `technical-project`, `ui-tests-v1.0.0-schema.json` for `ui-test-catalog`, `coverage-matrix-v1.0.0-schema.json` for `coverage-matrix`. Additionally, a `technical-project` source that is a raw collector file (no normalized `meta`/`content` envelope) fails with a message directing you to the [`living-doc-toolkit` `normalize-issues` step][toolkit-normalize]. `schema-path` is an advanced, bring-your-own override for that default and is unsupported — prefer normalizing your input instead.

## Action Outputs

| Output | Description |
|--------|-------------|
| `pdf_path` | Absolute path to the generated PDF |
| `html_path` | Absolute path to the debug HTML (only when `debug-html=true`) |
| `report_path` | Absolute path to `pdf_report.json` |

### Exit codes

| Code | Condition | Message prefix |
|------|-----------|----------------|
| 0 | Success | - |
| 1 | Invalid input (missing file, invalid JSON) | `Invalid input:` |
| 2 | Schema validation failure | `Schema validation failed:` |
| 3 | Template error (missing, invalid) | `Template error:` |
| 4 | Rendering error (WeasyPrint) | `Rendering failed:` |
| 5 | File I/O error (write failure) | `File I/O error:` |

## Developer Guide

For local setup, static analysis, testing, coverage, running the action locally, and the branch-naming convention, see [DEVELOPER.md](./DEVELOPER.md).

## How-to

### Source JSON

The action does not transform the source JSON — it is exposed to templates as `data` exactly as parsed. Each built-in document type expects a particular shape; see [examples/](./examples/) for runnable samples:

- [examples/generator-ready.json](./examples/generator-ready.json) — `technical-project`
- [examples/ui_tests.json](./examples/ui_tests.json) — `ui-test-catalog`
- [examples/coverage_matrix.json](./examples/coverage_matrix.json) — `coverage-matrix`

#### Schema validation

Every built-in `document-type` is validated by default against its vendored
schema — no `schema-path` needed:

| `document-type` | Input artifact | Vendored schema | Producer |
|-----------------|----------------|-----------------|----------|
| `technical-project` | `generator-ready.json` | `generator-ready-v1.0.0-schema.json` | `living-doc normalize-issues` |
| `ui-test-catalog` | `ui-tests.json` | `ui-tests-v1.0.0-schema.json` | `living-doc-collector-gh` `ui-tests` mode |
| `coverage-matrix` | `coverage-matrix.json` | `coverage-matrix-v1.0.0-schema.json` | `living-doc coverage-matrix` |

For `technical-project`, raw collector output (no normalized `meta`/`content`
envelope) additionally fails with a pointer to the
[`living-doc-toolkit` `normalize-issues` step][toolkit-normalize]. Built-in
schemas live in [generator/schemas/](./generator/schemas/):

```yaml
with:
  source-path: 'generator-ready.json'   # normalized by `living-doc normalize-issues`
  document-type: 'technical-project'
```

**Advanced / bring-your-own `schema-path` (unsupported).** Passing a custom
`schema-path` replaces the vendored default schema for whichever `document-type`
you selected. This is an escape hatch, not the recommended flow — the supported
path is to feed the toolkit-produced artifact for that `document-type` and let
default validation run:

```yaml
with:
  source-path: 'my-source.json'
  document-type: 'technical-project'
  schema-path: 'my/own-schema.json'   # advanced, unsupported override
```

#### Input schema-version compatibility

Where the `schema_version` lives depends on the `document-type`:

| `document-type` | `schema_version` location | Missing value |
|-----------------|---------------------------|---------------|
| `technical-project`, `coverage-matrix` | top-level `schema_version` (e.g. `"generator-ready-v1.0.0"`) | hard error (exit 1) |
| `ui-test-catalog` | top-level `schema_version` if present, else `metadata.original_metadata.schema_version` (written by `living-doc-collector-gh`, e.g. `"1.0.0"`) | tolerated — the vendored `ui-tests-v1.0.0-schema.json` pins the contract, so structural validation is the compatibility check |

When a `schema_version` is present, the action checks its embedded semantic
version against the supported range `>=1.0.0,<2.0.0`, **before** any optional
`schema-path` validation:

- **In range** — rendered normally.
- **Out of range** but parseable — a warning is logged and recorded in
  `pdf_report.json` (`warnings[]`, code `schema_version_out_of_range`); rendering
  still proceeds, so a newer canonical artifact is a best-effort render, not a
  hard stop.
- **`null`, blank, or unparseable** (or absent, for the types that require it) —
  the run fails fast with exit code 1 and a single structured
  `Invalid input: ... 'schema_version' ...` message.

Because the compatibility check runs first, a bundled `schema-path` that pins one
exact `schema_version` cannot pre-empt the out-of-range warning path with an
exit-code-2 `SchemaValidationError`.

The check lives in a PDF-independent helper
([generator/utils/version_compat.py](./generator/utils/version_compat.py)) — its
only third-party dependency is [`semver`](https://pypi.org/project/semver/) — so
other generators can reuse it verbatim.

### `coverage-matrix`: merge before you run

`coverage-matrix.json` is produced by the toolkit's `coverage-matrix` service,
which joins a technical project (User Stories + ACs) to a test catalog
(scenarios) on **AC ID**. That join is only valid when both sides describe the
**same** dataset.

**A cross-source coverage matrix is only valid on the merged dataset.** If the
matrix must span more than one source (a GitHub repo *and* an Azure DevOps
project, or GitHub issues *and* source-code `.feature` files), the sources must be
merged into a single `doc-source.json` / `ui-tests.json` pair **before**
`coverage-matrix` runs. This generator renders whatever `coverage-matrix.json` it
is given — it cannot detect or repair an unmerged one.

**The false-gap failure mode.** Running `coverage-matrix` per-source, while the
covering scenarios live in another source's catalog, does not merely miss the
cross-source coverage — it **reports every cross-source AC as an uncovered gap**.
The covering scenario is absent from the input, so the AC lands in the "no
scenario" bucket and `coverage_pct` drops. In the rendered PDF this false gap is
indistinguishable from a genuine coverage hole. A wall of uncovered ACs is the
signal to check that the `doc-source.json` and `ui-tests.json` behind the matrix
were produced from the *same* merged set of sources.

This depends on an authoring-time rule: **entity and AC IDs must be globally
unique across every source** — no `US-1` meaning one thing in a GitHub repo and
another in Azure DevOps. `coverage-matrix` cannot reconcile colliding IDs after
the fact.

See the toolkit's
[`coverage-matrix` service — "Multi-source coverage matrices"](https://github.com/AbsaOSS/living-doc-toolkit/blob/master/packages/services/coverage_matrix/README.md#multi-source-coverage-matrices--merge-before-you-run)
and the
[Living Doc Glossary — "ID uniqueness"](https://github.com/AbsaOSS/living-doc/blob/master/docs/guides/living-doc-glossary.md#id-uniqueness).

### Template customization

Templates always have a single entry point: `main.html.jinja`. They receive two variables:

- `data` — the raw parsed JSON (no Python-side transformation).
- `meta` — injected metadata: `document_title`, `generated_at` (ISO 8601 UTC), `source_file` (basename).

Three override levels are supported:

1. **Built-in only** — set `document-type`.
2. **Custom only** — set `template-path` to a self-contained directory (must include `main.html.jinja`).
3. **Partial override** — set both: your files win, missing partials fall back to the built-in set.

```jinja
<h1>{{ meta.document_title }}</h1>
<p>Generated: {{ meta.generated_at | format_datetime }}</p>

{% for item in data.get('items', []) | natural_sort(attribute='id') %}
  <h2>{{ item.id }}: {{ item.title }}</h2>
  <div>{{ item.description | markdown | safe }}</div>
{% endfor %}
```

#### Custom Jinja filters

- `markdown(text)` — convert Markdown to HTML.
- `format_datetime(value, fmt='%Y-%m-%d %H:%M')` — format an ISO 8601 timestamp.
- `default_if_none(value, fallback='')` — substitute a fallback for `None`.
- `natural_sort(items, attribute=None)` — human/natural ordering (so `US-2` precedes `US-10`).

See the full [template override guide](./docs/template-override-guide.md) for copying a built-in set, overriding partials, and troubleshooting.

### Troubleshooting

**`Invalid input: File '...' not found`** — `source-path` points to a missing file; verify the path.

**`Schema validation failed: ...`** — the source does not match the active schema. For `technical-project` this is `generator-ready-v1.0.0-schema.json` by default; if the file is raw collector output, run it through the [`living-doc-toolkit` `normalize-issues` step][toolkit-normalize] first. For other document types, fix the data or omit `schema-path` to skip validation.

**`Invalid input: 'schema_version' is absent ...`** / **`... unparseable 'schema_version' ...`** — every source must declare a parseable `schema_version` (for example `generator-ready-v1.0.0`); add or fix the key. `technical-project` and `coverage-matrix` require a top-level `schema_version`; `ui-test-catalog` does not (see [Input schema-version compatibility](#input-schema-version-compatibility)).

**`Template error: Template 'main.html.jinja' not found`** — a custom `template-path` lacks `main.html.jinja`; add it or also set `document-type` for fallback.

**`Rendering failed: ...`** — invalid HTML/CSS reached WeasyPrint; set `debug-html: 'true'` and inspect the saved HTML.

**`File I/O error: Permission denied`** — the output directory is not writable; change `output-path` or grant write permission.

## Contribution Guidelines

Contributions are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the bug-report, feature-request, branch-naming, and PR conventions. For development guidelines, see [DEVELOPER.md](./DEVELOPER.md).

### License Information

Licensed under the Apache License 2.0 — see [LICENSE](./LICENSE).

### Contact or Support Information

Maintained by [ABSA Group Limited](https://github.com/AbsaOSS). Open a [GitHub Issue](https://github.com/AbsaOSS/living-doc-generator-pdf/issues) for questions, bug reports, or feature requests.
