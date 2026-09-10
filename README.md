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

**Key features**
- 📄 Source-independent: renders raw JSON; no knowledge of GitHub, Jira, etc.
- 🎨 Template-driven: built-in sets plus full or partial custom overrides
- ✅ Optional validation: opt-in JSON Schema checking via `schema-path`
- ⚡ Deterministic: same input always produces the same output
- 🔍 Debug mode: save the intermediate HTML for troubleshooting
- 📊 Reporting: emits `pdf_report.json` with statistics

## Usage

### Prerequisites

- **Python 3.10 or later.**
- **System dependencies** (WeasyPrint): `libpango-1.0-0`, `libpangocairo-1.0-0`, `libgdk-pixbuf2.0-0`, `libffi-dev`, `libcairo2`. These are installed automatically by the action on Ubuntu runners.

### Adding the Action to Your Workflow

```yaml
- name: Generate PDF
  uses: AbsaOSS/living-doc-generator-pdf@v1
  with:
    source-path: 'doc-source.json'
    document-type: 'technical-project'
    output-path: 'documentation.pdf'
```

#### Full Example of Action Step Definition

```yaml
# .github/workflows/generate-docs.yml
name: Generate Documentation PDF

on:
  push:
    branches: [main]

jobs:
  generate-pdf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate PDF
        uses: AbsaOSS/living-doc-generator-pdf@v1
        with:
          source-path: 'doc-source.json'
          document-type: 'technical-project'
          output-path: 'documentation.pdf'
          document-title: 'Product Backlog'
          schema-path: 'generator/schemas/doc-issues-v1.0.0-schema.json'
          debug-html: 'true'
          verbose: 'true'

      - name: Upload PDF
        uses: actions/upload-artifact@v4
        with:
          name: documentation-pdf
          path: documentation.pdf
```

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
| `schema-path` | string (path) | No | - | JSON Schema for opt-in source validation |
| `debug-html` | boolean | No | `false` | Save the rendered HTML next to the PDF |
| `verbose` | boolean | No | `false` | Enable verbose logging |
| `pdf_ready_json` | string (path) | No | - | **Deprecated** alias for `source-path` |

At least one of `document-type` or `template-path` must be provided. When `document-title` is not set, the title is derived from the document type's default (e.g. "Technical Project") or the source file name.

The `technical-project` document type is **validated by default**: when no `schema-path` is given, the source is checked against the vendored `generator-ready-v1.0.0-schema.json`. A raw collector file (one with no normalized `meta`/`content` envelope) fails with a message directing you to the `living-doc-toolkit` normalization step. Pass an explicit `schema-path` to override the default.

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

`technical-project` is validated by default against the vendored
`generator-ready-v1.0.0-schema.json`; raw collector output (no normalized
`meta`/`content` envelope) fails with a pointer to the `living-doc-toolkit`
normalization step. For every other document type, validation is opt-in: pass
`schema-path` to validate the source before rendering; omit it to render as-is.
Built-in schemas live in [generator/schemas/](./generator/schemas/):

```yaml
with:
  source-path: 'generator-ready.json'
  document-type: 'technical-project'
  # schema-path optional here; pass one to override the default schema
```

#### Input schema-version compatibility

Every source JSON must declare a top-level `schema_version` (for example
`"generator-ready-v1.0.0"`) naming the input contract it targets. The action
checks the embedded semantic version against the supported range
`>=1.0.0,<2.0.0`, **before** any optional `schema-path` validation:

- **In range** — rendered normally.
- **Out of range** but parseable — a warning is logged and recorded in
  `pdf_report.json` (`warnings[]`, code `schema_version_out_of_range`); rendering
  still proceeds, so a newer canonical artifact is a best-effort render, not a
  hard stop.
- **Absent, `null`, blank, or unparseable** — the run fails fast with exit code 1
  and a single structured `Invalid input: ... 'schema_version' ...` message. A
  document with no declared contract is never rendered.

Because the compatibility check runs first, a bundled `schema-path` that pins one
exact `schema_version` cannot pre-empt the out-of-range warning path with an
exit-code-2 `SchemaValidationError`.

The check lives in a PDF-independent helper
([generator/utils/version_compat.py](./generator/utils/version_compat.py)) — its
only third-party dependency is [`semver`](https://pypi.org/project/semver/) — so
other generators can reuse it verbatim.

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

**`Schema validation failed: ...`** — the source does not match the active schema. For `technical-project` this is `generator-ready-v1.0.0-schema.json` by default; if the file is raw collector output, run it through the `living-doc-toolkit` normalization step first. For other document types, fix the data or omit `schema-path` to skip validation.

**`Invalid input: 'schema_version' is absent ...`** / **`... unparseable 'schema_version' ...`** — every source must declare a parseable `schema_version` (for example `generator-ready-v1.0.0`); add or fix the key. Omitting it is not allowed.

**`Template error: Template 'main.html.jinja' not found`** — a custom `template-path` lacks `main.html.jinja`; add it or also set `document-type` for fallback.

**`Rendering failed: ...`** — invalid HTML/CSS reached WeasyPrint; set `debug-html: 'true'` and inspect the saved HTML.

**`File I/O error: Permission denied`** — the output directory is not writable; change `output-path` or grant write permission.

## Contribution Guidelines

Contributions are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the bug-report, feature-request, branch-naming, and PR conventions. For development guidelines, see [DEVELOPER.md](./DEVELOPER.md).

### License Information

Licensed under the Apache License 2.0 — see [LICENSE](./LICENSE).

### Contact or Support Information

Maintained by [ABSA Group Limited](https://github.com/AbsaOSS). Open a [GitHub Issue](https://github.com/AbsaOSS/living-doc-generator-pdf/issues) for questions, bug reports, or feature requests.
