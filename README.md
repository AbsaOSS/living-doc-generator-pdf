# Living Doc Generator PDF

[![Build and Test](https://github.com/AbsaOSS/living-doc-generator-pdf/actions/workflows/test.yml/badge.svg)](https://github.com/AbsaOSS/living-doc-generator-pdf/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A source-agnostic GitHub Action that consumes structured JSON (`pdf_ready.json`) and produces professional PDF documentation using Jinja templates and WeasyPrint.

## Overview

The Living Doc Generator PDF is designed to be the final stage in a documentation pipeline. It takes a canonical JSON format (`pdf_ready.json`) containing all necessary documentation data and renders it into a beautifully formatted PDF using customizable Jinja2 templates.

**Key Features:**
- 📄 Source-independent: Consumes standardized JSON, no knowledge of GitHub, Azure DevOps, or other sources
- 🎨 Template-driven: Full control over PDF appearance via Jinja2 templates
- ⚡ Fast & deterministic: Same input always produces same output
- 🔍 Debug mode: Save intermediate HTML for troubleshooting
- 📊 Detailed reporting: Generates metadata report (`pdf_report.json`) with statistics

**Use Cases:**
- Generate stakeholder-ready documentation PDFs
- Create compliance documentation for audits
- Produce offline-friendly documentation archives
- Build custom documentation formats via templates

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
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate PDF
        uses: AbsaOSS/living-doc-generator-pdf@v1
        with:
          pdf_ready_json: 'examples/minimal_valid.json'
          output_path: 'documentation.pdf'

      - name: Upload PDF
        uses: actions/upload-artifact@v4
        with:
          name: documentation-pdf
          path: documentation.pdf
```

## Requirements

- **Python:** 3.14 or later
- **System Dependencies:** WeasyPrint requires system libraries:
  - `libpango-1.0-0`
  - `libpangocairo-1.0-0`
  - `libgdk-pixbuf2.0-0`
  - `libffi-dev`
  - `libcairo2`

These dependencies are automatically installed by the action on Ubuntu runners.

## Configuration

### Inputs

| Input Name | Type | Required | Default | Description |
|------------|------|----------|---------|-------------|
| `pdf_ready_json` | string (path) | **Yes** | - | Path to pdf_ready.json file |
| `output_path` | string (path) | No | `output.pdf` | Path for generated PDF file |
| `template_dir` | string (path) | No | _(empty)_ | Directory containing custom Jinja templates |
| `debug_html` | boolean | No | `false` | Save intermediate HTML as rendered.html |
| `verbose` | boolean | No | `false` | Enable verbose logging |

**Input Details:**
- `pdf_ready_json`: Must point to a valid JSON file following the canonical schema v1.0 (see [SPEC.md § 3.2](./SPEC.md#32-pdf-ready-json-schema-v10))
- `output_path`: Parent directory will be created if it doesn't exist
- `template_dir`: When provided, must contain `main.html.jinja`, `cover.html.jinja`, `user_story.html.jinja`, and `styles.css`
- `debug_html`: When `true`, saves rendered HTML next to output PDF as `{output}_rendered.html`
- `verbose`: Accepts `true`/`false`, `1`/`0`, `yes`/`no` (case-insensitive)

### Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `pdf_path` | string (path) | Absolute path to generated PDF file |
| `html_path` | string (path) | Absolute path to debug HTML (if `debug_html=true`) |
| `report_path` | string (path) | Absolute path to `pdf_report.json` |

**Output Details:**
- `pdf_path`: Always set on successful PDF generation
- `html_path`: Only set when `debug_html=true`
- `report_path`: Contains generation metadata, statistics, and any warnings

### Exit Codes

| Exit Code | Condition | Error Message Prefix |
|-----------|-----------|---------------------|
| 0 | Success | - |
| 1 | Invalid input (missing file, invalid JSON) | `Invalid input:` |
| 2 | Schema validation failure | `Schema validation failed:` |
| 3 | Template error (missing, invalid) | `Template error:` |
| 4 | Rendering error (WeasyPrint failure) | `Rendering failed:` |
| 5 | File I/O error (write failure) | `File I/O error:` |

## Example Workflows

### Basic Usage

```yaml
name: Generate PDF

on:
  push:
    branches: [main]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate PDF
        uses: AbsaOSS/living-doc-generator-pdf@v1
        with:
          pdf_ready_json: 'data/documentation.json'
          output_path: 'docs/output.pdf'
```

### Custom Templates

```yaml
name: Generate PDF with Custom Theme

on:
  push:
    branches: [main]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate PDF with custom templates
        uses: AbsaOSS/living-doc-generator-pdf@v1
        with:
          pdf_ready_json: 'data/documentation.json'
          output_path: 'docs/branded.pdf'
          template_dir: 'templates/custom'
```

### Debug Mode with HTML Output

```yaml
name: Generate PDF with Debug HTML

on:
  push:
    branches: [main]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate PDF with debug HTML
        id: generate
        uses: AbsaOSS/living-doc-generator-pdf@v1
        with:
          pdf_ready_json: 'data/documentation.json'
          output_path: 'docs/output.pdf'
          debug_html: 'true'
          verbose: 'true'

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: documentation
          path: |
            ${{ steps.generate.outputs.pdf_path }}
            ${{ steps.generate.outputs.html_path }}
            ${{ steps.generate.outputs.report_path }}
```

## PDF-Ready JSON Schema

The action expects a JSON file following the canonical schema v1.0. Here's a minimal example:

```json
{
  "schema_version": "1.0",
  "meta": {
    "document_title": "My Documentation",
    "document_version": "1.0.0",
    "generated_at": "2026-01-21T12:00:00Z",
    "source_set": ["github:myorg/myrepo"],
    "selection_summary": {
      "total_items": 5,
      "included_items": 5,
      "excluded_items": 0
    }
  },
  "content": {
    "user_stories": [
      {
        "id": "US-001",
        "title": "User login feature",
        "description": "As a user, I want to log in securely",
        "acceptance_criteria": [
          {
            "description": "User can enter credentials",
            "scenarios": []
          }
        ],
        "metadata": {
          "status": "implemented",
          "priority": "high"
        }
      }
    ]
  }
}
```

For complete schema details, see [SPEC.md § 3.2](./SPEC.md#32-pdf-ready-json-schema-v10).

### Generating pdf_ready.json

This action is source-agnostic and only consumes the `pdf_ready.json` format. To create this file from your documentation sources:

- **GitHub repositories:** Use [living-doc-collector-gh](https://github.com/AbsaOSS/living-doc-collector-gh) to extract documentation
- **Azure DevOps:** Use appropriate collector tools
- **Custom sources:** Generate JSON matching the canonical schema

## Template Customization

The action uses Jinja2 templates to render HTML before converting to PDF. You can customize the appearance by providing your own template pack.

### Template Pack Structure

A template pack must include these files:

```
my-templates/
├── main.html.jinja       # Main document template
├── cover.html.jinja      # Cover page template
├── user_story.html.jinja # Individual story template
└── styles.css            # CSS styling
```

### Available Template Variables

Templates receive a context object with these variables:

- `meta`: Document metadata (title, version, timestamp, etc.)
- `content`: User stories and documentation content
- `template_pack`: Template pack information

**Example template snippet:**
```jinja
<h1>{{ meta.document_title }}</h1>
<p>Version: {{ meta.document_version }}</p>
<p>Generated: {{ meta.generated_at|format_datetime }}</p>

{% for story in content.user_stories %}
  <div class="story">
    <h2>{{ story.id }}: {{ story.title }}</h2>
    <p>{{ story.description }}</p>
  </div>
{% endfor %}
```

### Available Jinja Filters

The action provides custom Jinja filters for formatting:

- `format_datetime(value)`: Format ISO 8601 timestamp as human-readable
- `markdown(text)`: Convert Markdown text to HTML

For complete template documentation, see [SPEC.md § 6](./SPEC.md#6-template-pack-specification).

## Troubleshooting

### Common Errors

**Error: `Invalid input: File 'data.json' not found`**
- **Cause:** The specified `pdf_ready_json` file doesn't exist
- **Fix:** Verify the file path is correct and the file exists in your repository

**Error: `Schema validation failed: Missing required field 'schema_version'`**
- **Cause:** The JSON file doesn't follow the canonical schema v1.0
- **Fix:** Ensure your JSON includes all required fields (see [SPEC.md § 3.2](./SPEC.md#32-pdf-ready-json-schema-v10))

**Error: `Template error: Template 'main.html.jinja' not found`**
- **Cause:** Custom template directory is missing required templates
- **Fix:** Ensure `template_dir` contains all required files, or omit the input to use built-in templates

**Error: `Rendering failed: WeasyPrint could not render HTML`**
- **Cause:** Invalid HTML or CSS in templates
- **Fix:** Use `debug_html: true` to inspect the rendered HTML and identify syntax errors

**Error: `File I/O error: Permission denied`**
- **Cause:** No write permission for output directory
- **Fix:** Ensure the GitHub Action has write permissions, or change `output_path` to a writable location

### Debug Tips

1. **Enable verbose logging:**
   ```yaml
   with:
     verbose: 'true'
   ```

2. **Save debug HTML:**
   ```yaml
   with:
     debug_html: 'true'
   ```

3. **Check pdf_report.json:**
   The report file contains generation statistics and warnings that may help diagnose issues.

4. **Validate JSON locally:**
   Use a JSON validator or the verification scripts in `verifications/verify_schema_examples.py`.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/AbsaOSS/living-doc-generator-pdf.git
cd living-doc-generator-pdf

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Run verification scripts
python verifications/verify_schema_examples.py
python verifications/verify_templates.py
python verifications/verify_error_messages.py
```

For detailed development guidelines, see [DEVELOPER.md](./DEVELOPER.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

---

**Maintained by:** [ABSA Group Limited](https://github.com/AbsaOSS)
**Documentation:** [SPEC.md](./SPEC.md) | [TASKS.md](./TASKS.md)
