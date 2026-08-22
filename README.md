# Living Doc Generator PDF

[![Build and Test](https://github.com/AbsaOSS/living-doc-generator-pdf/actions/workflows/test.yml/badge.svg)](https://github.com/AbsaOSS/living-doc-generator-pdf/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A source-agnostic GitHub Action that renders **any** structured JSON into a professional PDF using Jinja2 templates and WeasyPrint. It ships with three built-in document types and supports fully custom template packs.

## Overview

The action is a generic JSON-to-PDF engine: you provide a JSON source file and either a built-in `document-type` or your own `template-path`. The raw JSON is passed to the templates unchanged as `data`, alongside injected `meta` (title, timestamp, source file name).






**Built-in document types**

| `document-type` | Purpose | Typical source |
|-----------------|---------|----------------|
| `user-stories` | User Stories with acceptance criteria | `doc-source.json` |
| `ui-test-catalog` | BDD/UI test scenarios grouped by feature file | `ui-tests.json` |
| `coverage-matrix` | AC-to-test coverage report | `coverage-matrix.json` |

**Key features**
- 📄 Source-independent: renders raw JSON; no knowledge of GitHub, Jira, etc.
- 🎨 Template-driven: built-in sets plus full or partial custom overrides
- ✅ Optional validation: opt-in JSON Schema checking via `schema-path`
- ⚡ Deterministic: same input always produces the same output
- 🔍 Debug mode: save the intermediate HTML for troubleshooting
- 📊 Reporting: emits `pdf_report.json` with statistics

## Quick Start

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
          document-type: 'user-stories'
          output-path: 'documentation.pdf'

      - name: Upload PDF
        uses: actions/upload-artifact@v4
        with:
          name: documentation-pdf
          path: documentation.pdf
```

## Requirements

- **Python:** 3.14 or later
- **System dependencies** (WeasyPrint): `libpango-1.0-0`, `libpangocairo-1.0-0`, `libgdk-pixbuf2.0-0`, `libffi-dev`, `libcairo2`. These are installed automatically by the action on Ubuntu runners.

## Configuration

### Inputs

| Input | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source-path` | string (path) | **Yes** | - | Path to the source JSON file to render |
| `document-type` | string | Conditional | - | Built-in set: `user-stories`, `ui-test-catalog`, or `coverage-matrix` |
| `template-path` | string (path) | Conditional | - | Custom template directory (overrides or extends a built-in set) |
| `output-path` | string (path) | No | `output.pdf` | Path for the generated PDF |
| `document-title` | string | No | _(derived)_ | Cover-page title |
| `schema-path` | string (path) | No | - | JSON Schema for opt-in source validation |
| `debug-html` | boolean | No | `false` | Save the rendered HTML next to the PDF |
| `verbose` | boolean | No | `false` | Enable verbose logging |
| `pdf_ready_json` | string (path) | No | - | **Deprecated** alias for `source-path` |

At least one of `document-type` or `template-path` must be provided. When neither `document-title` is set, the title is derived from the document type's default (e.g. "User Stories") or the source file name.

### Outputs

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

## Source JSON

The action does not transform the source JSON — it is exposed to templates as `data` exactly as parsed. Each built-in document type expects a particular shape; see [examples/](./examples/) for runnable samples:

- [examples/user_stories.json](./examples/user_stories.json) — `user-stories`
- [examples/ui_tests.json](./examples/ui_tests.json) — `ui-test-catalog`
- [examples/coverage_matrix.json](./examples/coverage_matrix.json) — `coverage-matrix`

### Optional schema validation

Validation is opt-in. Pass `schema-path` to validate the source before rendering; omit it to render as-is. Built-in schemas live in [generator/schemas/](./generator/schemas/):

```yaml
with:
  source-path: 'doc-source.json'
  document-type: 'user-stories'
  schema-path: 'generator/schemas/doc-issues-v1.0.0-schema.json'
```

## Template customization

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

### Custom Jinja filters

- `markdown(text)` — convert Markdown to HTML.
- `format_datetime(value, fmt='%Y-%m-%d %H:%M')` — format an ISO 8601 timestamp.
- `default_if_none(value, fallback='')` — substitute a fallback for `None`.
- `natural_sort(items, attribute=None)` — human/natural ordering (so `US-2` precedes `US-10`).

See the full [template override guide](./docs/template-override-guide.md) for copying a built-in set, overriding partials, and troubleshooting.

## Troubleshooting

**`Invalid input: File '...' not found`** — `source-path` points to a missing file; verify the path.

**`Schema validation failed: ...`** — the source does not match the schema passed via `schema-path`; fix the data or omit `schema-path` to skip validation.

**`Template error: Template 'main.html.jinja' not found`** — a custom `template-path` lacks `main.html.jinja`; add it or also set `document-type` for fallback.

**`Rendering failed: ...`** — invalid HTML/CSS reached WeasyPrint; set `debug-html: 'true'` and inspect the saved HTML.

**`File I/O error: Permission denied`** — the output directory is not writable; change `output-path` or grant write permission.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md). For development guidelines, see [DEVELOPER.md](./DEVELOPER.md).

```bash
git clone https://github.com/AbsaOSS/living-doc-generator-pdf.git
cd living-doc-generator-pdf
pip install -r requirements.txt
pytest tests/
```

## License

Licensed under the Apache License 2.0 — see [LICENSE](./LICENSE).

---

**Maintained by:** [ABSA Group Limited](https://github.com/AbsaOSS)
**Documentation:** [spec.md](./spec.md) | [DEVELOPER.md](./DEVELOPER.md) | [Template override guide](./docs/template-override-guide.md)
