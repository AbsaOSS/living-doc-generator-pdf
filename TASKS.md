# Living Documentation PDF Generator - Implementation Tasks

**Specification Reference:** [SPEC.md](./SPEC.md)  
**Version:** 1.0  
**Last Updated:** 2026-01-21

---

## Overview

This document breaks down the implementation of the Living Documentation PDF Generator into discrete, testable tasks with specific acceptance criteria and verification methods.

---

## Task Breakdown

### Phase 1: Core Infrastructure & Schema Validation

#### Task 1.1: Define JSON Schema for pdf_ready.json

**Owner:** Specification Master (complete) ✓  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 3.2](./SPEC.md#32-pdf-ready-json-schema-v10)

**Acceptance Criteria:**
- [ ] JSON Schema file created at `generator/schemas/pdf_ready_v1.0.json`
- [ ] Schema enforces all required fields from SPEC.md § 3.2.2 and § 3.2.3
- [ ] Schema validates data types (strings, integers, arrays, objects)
- [ ] Schema validates value constraints (non-empty strings, valid URLs, ISO timestamps)
- [ ] Schema rejects unknown `schema_version` values (only "1.0" allowed)

**Verification:**
- `tests/unit/test_schema_validation.py::test_valid_schema_examples` - Valid examples pass
- `tests/unit/test_schema_validation.py::test_invalid_schema_examples` - Invalid examples rejected with specific errors
- `verifications/verify_schema_examples.py` - Validate example JSON files against schema

**Example Test Scenario:**
```python
# Valid minimal example
valid_json = {
    "schema_version": "1.0",
    "meta": {
        "document_title": "Test Doc",
        "document_version": "1.0.0",
        "generated_at": "2026-01-21T12:00:00Z",
        "source_set": ["github:test/repo"],
        "selection_summary": {"total_items": 1, "included_items": 1, "excluded_items": 0}
    },
    "content": {"user_stories": []}
}
assert validate_schema(valid_json) == True

# Invalid: missing schema_version
invalid_json = {"meta": {...}, "content": {...}}
with pytest.raises(ValidationError, match="Missing required field 'schema_version'"):
    validate_schema(invalid_json)
```

---

#### Task 1.2: Implement Schema Validator

**Owner:** Senior Developer  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 3.2](./SPEC.md#32-pdf-ready-json-schema-v10), [SPEC.md § 3.1.3](./SPEC.md#313-exit-codes)

**Acceptance Criteria:**
- [ ] Module `generator/schema_validator.py` created
- [ ] Function `validate_pdf_ready_json(file_path: str) -> dict` implemented
- [ ] Validation uses `jsonschema` library with JSON Schema from Task 1.1
- [ ] Clear error messages for validation failures (exit code 2)
- [ ] Error messages follow format: `Schema validation failed: {detail}. {guidance}`
- [ ] Returns parsed JSON dict on success

**Verification:**
- `tests/unit/test_schema_validator.py::test_validate_valid_json` - Valid JSON passes
- `tests/unit/test_schema_validator.py::test_validate_missing_schema_version` - Error message check
- `tests/unit/test_schema_validator.py::test_validate_invalid_timestamp` - Timestamp validation
- `tests/integration/test_error_codes.py::test_schema_validation_exit_code` - Exit code 2

**Error Message Examples:**
```
Schema validation failed: Missing required field 'schema_version'. Ensure JSON follows canonical schema v1.0.
Schema validation failed: 'generated_at' is not a valid ISO 8601 timestamp. Use format: YYYY-MM-DDTHH:MM:SSZ.
Schema validation failed: 'document_title' must be a non-empty string. Provide a valid title.
```

---

#### Task 1.3: Update ActionInputs for New Contract

**Owner:** Senior Developer  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 3.1.1](./SPEC.md#311-action-inputs)

**Acceptance Criteria:**
- [ ] `generator/action_inputs.py` updated with new input methods:
  - `get_pdf_ready_json() -> str` - path to pdf_ready.json
  - `get_output_path() -> str` - path for output PDF (default: "output.pdf")
  - `get_template_dir() -> Optional[str]` - custom template directory
  - `get_debug_html() -> bool` - save debug HTML flag
  - `get_verbose() -> bool` - verbose logging flag
- [ ] Old inputs (source_path, document_title) deprecated or removed
- [ ] Input validation raises ValueError with clear messages for invalid inputs
- [ ] Constants updated in `generator/utils/constants.py`

**Verification:**
- `tests/unit/test_action_inputs.py::test_get_pdf_ready_json` - Input reading
- `tests/unit/test_action_inputs.py::test_get_template_dir_optional` - Optional input
- `tests/unit/test_action_inputs.py::test_get_debug_html_boolean` - Boolean parsing
- `tests/unit/test_action_inputs.py::test_validate_inputs_missing_file` - Validation error

**Example Usage:**
```python
from generator.action_inputs import ActionInputs

# Environment: INPUT_PDF_READY_JSON=/workspace/data.json
json_path = ActionInputs.get_pdf_ready_json()  # "/workspace/data.json"
debug = ActionInputs.get_debug_html()          # False
```

---

### Phase 2: Template Engine & Rendering

#### Task 2.1: Create Built-in Template Pack

**Owner:** Senior Developer  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 3.4.1](./SPEC.md#341-built-in-template-pack)

**Acceptance Criteria:**
- [ ] Directory `generator/templates/` created with structure:
  ```
  generator/templates/
  ├── main.html.jinja
  ├── cover.html.jinja
  ├── user_story.html.jinja
  ├── styles.css
  └── assets/
      ├── fonts/
      │   └── DejaVuSans.ttf
      └── images/
          └── logo.png
  ```
- [ ] `main.html.jinja` renders complete HTML5 document
- [ ] `cover.html.jinja` renders cover page with metadata from `meta` section
- [ ] `user_story.html.jinja` renders individual user story with all sections
- [ ] `styles.css` provides professional styling (headers, spacing, page breaks)
- [ ] Font files included (DejaVu Sans family) and referenced in CSS
- [ ] Templates use only variables from canonical schema (SPEC.md § 3.2)

**Verification:**
- `verifications/verify_built_in_templates.py` - Template syntax check
- `tests/unit/test_template_rendering.py::test_render_cover_page` - Cover page rendering
- `tests/unit/test_template_rendering.py::test_render_user_story` - User story rendering
- Manual visual inspection of rendered HTML

**Template Variables Contract:**
```jinja
{# Available in all templates #}
{{ schema_version }}           {# "1.0" #}
{{ meta.document_title }}      {# string #}
{{ meta.document_version }}    {# string #}
{{ meta.generated_at }}        {# ISO timestamp #}
{{ content.user_stories }}     {# array of user story objects #}

{# User story template variables #}
{{ story.id }}                 {# canonical ID #}
{{ story.title }}              {# string #}
{{ story.state }}              {# string #}
{{ story.sections.description }} {# Markdown string #}
{{ story.sections.acceptance_criteria }} {# Markdown string #}
```

---

#### Task 2.2: Implement Template Renderer

**Owner:** Senior Developer  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 3.4](./SPEC.md#34-template-pack-structure)

**Acceptance Criteria:**
- [ ] Module `generator/template_renderer.py` created
- [ ] Class `TemplateRenderer` with methods:
  - `__init__(template_dir: Optional[str])` - initialize with built-in or custom templates
  - `render(pdf_ready_data: dict) -> str` - render HTML from JSON data
- [ ] Jinja2 environment configured with:
  - Autoescape enabled
  - Custom filters: `markdown`, `format_datetime`
  - Template loader from built-in or custom directory
- [ ] Custom template overrides work (custom templates override built-in)
- [ ] Missing custom templates fall back to built-in defaults
- [ ] Template errors raise clear exceptions (exit code 3)

**Verification:**
- `tests/unit/test_template_renderer.py::test_render_with_built_in_templates` - Built-in rendering
- `tests/unit/test_template_renderer.py::test_render_with_custom_templates` - Custom override
- `tests/unit/test_template_renderer.py::test_missing_template_error` - Error handling
- `tests/integration/test_custom_templates.py::test_partial_override` - Fallback behavior

**Error Message Examples:**
```
Template error: Template 'main.html.jinja' not found. Check template_dir path or use default templates.
Template error: Syntax error in 'user_story.html.jinja' at line 42. Fix template syntax.
```

---

#### Task 2.3: Implement Markdown Filter

**Owner:** Senior Developer  
**Priority:** High  
**Spec Reference:** [SPEC.md § 3.4.2](./SPEC.md#342-custom-template-pack)

**Acceptance Criteria:**
- [ ] Jinja2 filter `markdown` implemented in `generator/filters.py`
- [ ] Filter converts Markdown to HTML using `markdown` library
- [ ] Filter handles `None` and empty string gracefully (returns empty string)
- [ ] Filter escapes HTML in Markdown output to prevent injection
- [ ] Filter registered in `TemplateRenderer` Jinja2 environment

**Verification:**
- `tests/unit/test_filters.py::test_markdown_filter_basic` - Basic Markdown conversion
- `tests/unit/test_filters.py::test_markdown_filter_lists` - Lists and checkboxes
- `tests/unit/test_filters.py::test_markdown_filter_none` - None handling
- `tests/unit/test_filters.py::test_markdown_filter_escaping` - HTML escaping

**Example Usage:**
```jinja
{# Template usage #}
<div class="description">
  {{ story.sections.description | markdown }}
</div>

{# Input: "## Heading\n- Item 1\n- Item 2" #}
{# Output: <h2>Heading</h2><ul><li>Item 1</li><li>Item 2</li></ul> #}
```

---

### Phase 3: PDF Generation with WeasyPrint

#### Task 3.1: Implement PDF Generator

**Owner:** Senior Developer  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 3.5](./SPEC.md#35-asset-resolution)

**Acceptance Criteria:**
- [ ] Module `generator/pdf_generator.py` created
- [ ] Class `PdfGenerator` refactored with new methods:
  - `generate_pdf(html: str, output_path: str, template_dir: str) -> None`
- [ ] WeasyPrint integration configured:
  - Base URL set to template directory for asset resolution
  - Font loading from `assets/fonts/` directory
  - PDF metadata embedded (title, version, creation date)
- [ ] PDF output valid and openable in standard viewers (Adobe, Chrome, Firefox)
- [ ] Rendering errors raise clear exceptions (exit code 4)

**Verification:**
- `tests/integration/test_pdf_generation.py::test_generate_pdf_minimal` - Minimal PDF
- `tests/integration/test_pdf_generation.py::test_generate_pdf_with_stories` - Full PDF with user stories
- `tests/integration/test_pdf_generation.py::test_pdf_metadata` - Metadata embedded
- `verifications/verify_pdf_output.py` - PDF quality checks (fonts, metadata, structure)

**Error Message Examples:**
```
Rendering failed: WeasyPrint could not load font 'DejaVuSans.ttf'. Verify font files are present in assets directory.
Rendering failed: CSS parsing error in 'styles.css' at line 15. Fix CSS syntax.
```

---

#### Task 3.2: Implement Debug HTML Output

**Owner:** Senior Developer  
**Priority:** Medium  
**Spec Reference:** [SPEC.md § 3.1.1](./SPEC.md#311-action-inputs)

**Acceptance Criteria:**
- [ ] When `debug_html=true`, rendered HTML saved to file
- [ ] HTML filename is `{pdf_basename}_rendered.html` (e.g., `output_rendered.html`)
- [ ] HTML file includes all CSS and assets inline or with working relative paths
- [ ] HTML viewable in browser with correct rendering
- [ ] Action output `html_path` set when debug HTML generated

**Verification:**
- `tests/integration/test_debug_html.py::test_debug_html_saved` - HTML file created
- `tests/integration/test_debug_html.py::test_debug_html_viewable` - HTML valid
- `tests/integration/test_debug_html.py::test_debug_html_not_saved_by_default` - Not saved by default

**Example:**
```bash
# Input: debug_html=true, output_path=docs/report.pdf
# Output files:
# - docs/report.pdf
# - docs/report_rendered.html
```

---

#### Task 3.3: Implement PDF Report Generator

**Owner:** Senior Developer  
**Priority:** High  
**Spec Reference:** [SPEC.md § 3.3](./SPEC.md#33-pdf-report-json-schema)

**Acceptance Criteria:**
- [ ] Module `generator/report_generator.py` created
- [ ] Function `generate_pdf_report(...)` creates `pdf_report.json`
- [ ] Report includes all required fields from SPEC.md § 3.3
- [ ] Report includes warnings for missing user story sections
- [ ] Report includes file size and user story count statistics
- [ ] Action output `report_path` set to `pdf_report.json` path

**Verification:**
- `tests/unit/test_report_generator.py::test_generate_report_success` - Successful report
- `tests/unit/test_report_generator.py::test_generate_report_with_warnings` - Warnings included
- `tests/integration/test_pdf_generation.py::test_pdf_report_created` - Report file created

**Example Report:**
```json
{
  "schema_version": "1.0",
  "generated_at": "2026-01-21T12:05:00Z",
  "input_file": "/workspace/pdf_ready.json",
  "output_file": "/workspace/output.pdf",
  "template_pack": {"type": "built-in", "path": "built-in"},
  "statistics": {
    "user_story_count": 12,
    "total_pages": 45,
    "file_size_bytes": 2457600
  },
  "errors": [],
  "warnings": [
    {
      "level": "warning",
      "message": "User story 'github:AbsaOSS/project#99' has no acceptance_criteria section",
      "context": "user_stories[5]"
    }
  ]
}
```

---

### Phase 4: Error Handling & Integration

#### Task 4.1: Implement Comprehensive Error Handling

**Owner:** Senior Developer  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 3.1.3](./SPEC.md#313-exit-codes), [SPEC.md § 5.2](./SPEC.md#52-error-handling-strategy)

**Acceptance Criteria:**
- [ ] All error types from SPEC.md § 3.1.3 implemented with correct exit codes:
  - Exit code 1: Invalid input (missing file, invalid JSON)
  - Exit code 2: Schema validation failure
  - Exit code 3: Template error
  - Exit code 4: Rendering error
  - Exit code 5: File I/O error
- [ ] Error messages follow format: `{prefix} {detail}. {guidance}`
- [ ] All exceptions caught and converted to appropriate exit codes in `main.py`
- [ ] Logging includes stack traces for debugging (when verbose=true)

**Verification:**
- `tests/integration/test_error_handling.py::test_invalid_json_exit_code` - Exit code 1
- `tests/integration/test_error_handling.py::test_schema_validation_exit_code` - Exit code 2
- `tests/integration/test_error_handling.py::test_template_error_exit_code` - Exit code 3
- `tests/integration/test_error_handling.py::test_rendering_error_exit_code` - Exit code 4
- `tests/integration/test_error_handling.py::test_file_io_error_exit_code` - Exit code 5
- `verifications/verify_error_messages.py` - Error message format consistency

---

#### Task 4.2: Update Main Entrypoint

**Owner:** Senior Developer  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 5.1](./SPEC.md#51-processing-pipeline)

**Acceptance Criteria:**
- [ ] `main.py` refactored to implement processing pipeline from SPEC.md § 5.1:
  1. Load and parse pdf_ready.json
  2. Validate against schema v1.0
  3. Load template pack
  4. Render HTML using Jinja2
  5. Save debug HTML (if enabled)
  6. Render PDF using WeasyPrint
  7. Generate pdf_report.json
  8. Set action outputs
- [ ] All error types handled with correct exit codes
- [ ] Action outputs set correctly (`pdf_path`, `html_path`, `report_path`)
- [ ] Logging at INFO level for normal operation
- [ ] Verbose logging when `verbose=true`

**Verification:**
- `tests/integration/test_main_entrypoint.py::test_end_to_end_success` - Full pipeline success
- `tests/integration/test_main_entrypoint.py::test_action_outputs_set` - Outputs verified
- Manual CI run with example workflow

---

#### Task 4.3: Create Example JSON Files

**Owner:** Specification Master  
**Priority:** High  
**Spec Reference:** [SPEC.md § 3.2.4](./SPEC.md#324-complete-example)

**Acceptance Criteria:**
- [ ] Directory `examples/` created with example JSON files:
  - `examples/minimal_valid.json` - Minimal valid pdf_ready.json
  - `examples/full_example.json` - Complete example with all fields
  - `examples/multiple_stories.json` - 10+ user stories for realistic testing
  - `examples/invalid_missing_schema.json` - Invalid example (missing schema_version)
  - `examples/invalid_bad_timestamp.json` - Invalid example (bad timestamp)
- [ ] All valid examples pass schema validation
- [ ] All invalid examples fail with expected error messages

**Verification:**
- `verifications/verify_schema_examples.py` - Validate all example files
- `tests/integration/test_example_files.py::test_valid_examples_render` - Valid examples render to PDF

---

### Phase 5: Documentation & GitHub Action

#### Task 5.1: Create Action Definition (action.yml)

**Owner:** DevOps Engineer  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 3.1](./SPEC.md#31-github-action-interface)

**Acceptance Criteria:**
- [ ] File `action.yml` created at repository root
- [ ] Action metadata defined (name, description, branding)
- [ ] All inputs defined with descriptions and defaults (from SPEC.md § 3.1.1)
- [ ] All outputs defined with descriptions (from SPEC.md § 3.1.2)
- [ ] Action runs using `composite` or `docker` strategy
- [ ] Dependencies installed correctly (Jinja2, WeasyPrint, etc.)

**Verification:**
- `.github/workflows/test.yml` - CI workflow using action
- `.github/workflows/example.yml` - Example usage workflow
- Manual test in separate repository

**Example action.yml:**
```yaml
name: 'Living Doc Generator PDF'
description: 'Generate professional PDF documentation from canonical JSON'
branding:
  icon: 'file-text'
  color: 'blue'

inputs:
  pdf_ready_json:
    description: 'Path to pdf_ready.json file'
    required: true
  output_path:
    description: 'Path for generated PDF file'
    required: false
    default: 'output.pdf'
  template_dir:
    description: 'Directory containing custom Jinja templates'
    required: false
  debug_html:
    description: 'Save intermediate HTML as rendered.html'
    required: false
    default: 'false'

outputs:
  pdf_path:
    description: 'Absolute path to generated PDF file'
  html_path:
    description: 'Absolute path to debug HTML (if debug_html=true)'
  report_path:
    description: 'Absolute path to pdf_report.json'

runs:
  using: 'composite'
  steps:
    - name: Install dependencies
      run: pip install -r requirements.txt
      shell: bash
    - name: Run PDF generator
      run: python main.py
      shell: bash
```

---

#### Task 5.2: Update README with New Contract

**Owner:** Senior Developer  
**Priority:** High  
**Spec Reference:** [SPEC.md § 3.1](./SPEC.md#31-github-action-interface)

**Acceptance Criteria:**
- [ ] README.md updated with sections:
  - Overview (purpose, use cases)
  - Quick Start (minimal example)
  - Requirements (Python, dependencies)
  - Configuration (inputs table, outputs table)
  - Example Workflows (basic, custom templates, debug mode)
  - Troubleshooting (common errors)
- [ ] Example workflow demonstrates basic usage
- [ ] Example workflow demonstrates custom template usage
- [ ] Links to SPEC.md for detailed contracts
- [ ] Mirrors structure of `AbsaOSS/generate-release-notes` README

**Verification:**
- Manual review for clarity and completeness
- Test example workflows in CI

**Example Quick Start:**
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
          pdf_ready_json: 'data/pdf_ready.json'
          output_path: 'docs/documentation.pdf'
      
      - name: Upload PDF
        uses: actions/upload-artifact@v4
        with:
          name: documentation-pdf
          path: docs/documentation.pdf
```

---

#### Task 5.3: Create Verification Scripts

**Owner:** SDET  
**Priority:** High  
**Spec Reference:** [SPEC.md § 8.3](./SPEC.md#83-verification-scripts)

**Acceptance Criteria:**
- [ ] Directory `verifications/` created with scripts:
  - `verify_schema_examples.py` - Validate all example JSON files
  - `verify_pdf_output.py` - PDF quality checks (fonts, metadata, structure)
  - `verify_error_messages.py` - Error message format consistency
  - `verify_templates.py` - Template syntax and completeness
- [ ] All scripts exit with code 0 on success, non-zero on failure
- [ ] All scripts produce clear output (PASS/FAIL per check)
- [ ] Scripts can run in CI as quality gates

**Verification:**
- Run scripts manually and verify output
- Add scripts to CI workflow as quality gate step

**Example Script:**
```python
#!/usr/bin/env python3
"""Verify all example JSON files against schema."""

import sys
from pathlib import Path
from generator.schema_validator import validate_pdf_ready_json

def main():
    examples_dir = Path("examples")
    valid_examples = [
        "minimal_valid.json",
        "full_example.json",
        "multiple_stories.json"
    ]
    
    failures = []
    for example in valid_examples:
        try:
            validate_pdf_ready_json(examples_dir / example)
            print(f"✓ {example} - PASS")
        except Exception as e:
            print(f"✗ {example} - FAIL: {e}")
            failures.append(example)
    
    if failures:
        print(f"\n{len(failures)} validation(s) failed")
        sys.exit(1)
    else:
        print(f"\nAll {len(valid_examples)} validations passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

### Phase 6: Testing & Quality Assurance

#### Task 6.1: Achieve 80%+ Unit Test Coverage

**Owner:** SDET  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 8.1](./SPEC.md#81-unit-tests)

**Acceptance Criteria:**
- [ ] Unit tests cover all modules:
  - `generator/schema_validator.py`
  - `generator/action_inputs.py`
  - `generator/template_renderer.py`
  - `generator/filters.py`
  - `generator/report_generator.py`
- [ ] Coverage ≥ 80% overall
- [ ] Coverage ≥ 90% for schema_validator and action_inputs (critical modules)
- [ ] All tests pass locally and in CI
- [ ] Tests use mocking for file I/O and external dependencies

**Verification:**
- `pytest --cov=generator --cov-report=html --cov-fail-under=80`
- Review coverage report for untested lines

---

#### Task 6.2: Create Integration Tests

**Owner:** SDET  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 8.2](./SPEC.md#82-integration-tests)

**Acceptance Criteria:**
- [ ] Integration test suite created in `tests/integration/`:
  - `test_pdf_generation.py` - End-to-end PDF generation scenarios
  - `test_custom_templates.py` - Custom template override scenarios
  - `test_error_handling.py` - Error scenarios with exit codes
  - `test_edge_cases.py` - Large files, empty arrays, edge cases
  - `test_debug_html.py` - Debug HTML output scenarios
- [ ] Tests use real file system (not mocked)
- [ ] Tests verify actual PDF output (file exists, valid structure)
- [ ] All integration tests pass in CI environment

**Verification:**
- `pytest tests/integration/`
- Manual review of generated test artifacts (PDFs, HTMLs)

---

#### Task 6.3: CI/CD Workflow Integration

**Owner:** DevOps Engineer  
**Priority:** Critical  
**Spec Reference:** [SPEC.md § 6](./SPEC.md#6-phase-by-phase-acceptance-criteria)

**Acceptance Criteria:**
- [ ] `.github/workflows/test.yml` updated to:
  - Run unit tests with coverage reporting
  - Run integration tests
  - Run verification scripts
  - Upload test artifacts (coverage report, example PDFs)
- [ ] CI fails if coverage < 80%
- [ ] CI fails if any verification script fails
- [ ] CI passes on main branch and PRs

**Verification:**
- Trigger CI workflow and verify all steps pass
- Review uploaded artifacts in GitHub Actions

---

## Verification Matrix

| Task | Unit Tests | Integration Tests | Verification Script | Manual Testing |
|------|------------|-------------------|---------------------|----------------|
| 1.1 Schema Definition | ✓ | - | ✓ | - |
| 1.2 Schema Validator | ✓ | ✓ | - | - |
| 1.3 Action Inputs | ✓ | - | - | - |
| 2.1 Template Pack | ✓ | - | ✓ | ✓ |
| 2.2 Template Renderer | ✓ | ✓ | - | - |
| 2.3 Markdown Filter | ✓ | - | - | - |
| 3.1 PDF Generator | - | ✓ | ✓ | ✓ |
| 3.2 Debug HTML | - | ✓ | - | ✓ |
| 3.3 PDF Report | ✓ | ✓ | - | - |
| 4.1 Error Handling | - | ✓ | ✓ | - |
| 4.2 Main Entrypoint | - | ✓ | - | ✓ |
| 4.3 Example Files | - | ✓ | ✓ | - |
| 5.1 Action Definition | - | - | - | ✓ |
| 5.2 README Update | - | - | - | ✓ |
| 5.3 Verification Scripts | - | - | ✓ | ✓ |
| 6.1 Unit Coverage | ✓ | - | - | - |
| 6.2 Integration Tests | - | ✓ | - | - |
| 6.3 CI/CD Integration | - | - | - | ✓ |

---

## Definition of Done Checklist

A task is considered complete when:

- [ ] All acceptance criteria met
- [ ] All specified tests written and passing
- [ ] Code reviewed and approved (if applicable)
- [ ] Documentation updated (if applicable)
- [ ] Verification scripts pass (if applicable)
- [ ] CI/CD pipeline passes
- [ ] Changes committed and pushed to feature branch

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| WeasyPrint font loading fails in CI | High | Include fonts in repo, test in CI environment early |
| Large JSON files cause memory issues | Medium | Implement streaming JSON parsing if needed |
| Custom templates break built-in rendering | Medium | Comprehensive fallback mechanism, integration tests |
| PDF metadata not embedded correctly | Low | Use WeasyPrint metadata API, verify in tests |
| Schema validation performance slow | Low | Profile and optimize if needed, cache schema |

---

## Dependencies Between Tasks

```
Phase 1 (Core Infrastructure)
├── 1.1 Schema Definition
│   └── 1.2 Schema Validator
│       └── 1.3 Action Inputs
│           └── Phase 2 (Template Engine)
│
Phase 2 (Template Engine)
├── 2.1 Template Pack
│   └── 2.2 Template Renderer
│       └── 2.3 Markdown Filter
│           └── Phase 3 (PDF Generation)
│
Phase 3 (PDF Generation)
├── 3.1 PDF Generator
├── 3.2 Debug HTML
└── 3.3 PDF Report
    └── Phase 4 (Integration)

Phase 4 (Integration)
├── 4.1 Error Handling
├── 4.2 Main Entrypoint
└── 4.3 Example Files
    └── Phase 5 (Documentation)

Phase 5 (Documentation)
├── 5.1 Action Definition
├── 5.2 README Update
└── 5.3 Verification Scripts
    └── Phase 6 (Testing)

Phase 6 (Testing)
├── 6.1 Unit Coverage
├── 6.2 Integration Tests
└── 6.3 CI/CD Integration
```

---

## Timeline Estimate

| Phase | Tasks | Estimated Effort | Dependencies |
|-------|-------|-----------------|--------------|
| Phase 1 | 3 tasks | 2-3 days | None |
| Phase 2 | 3 tasks | 3-4 days | Phase 1 complete |
| Phase 3 | 3 tasks | 3-4 days | Phase 2 complete |
| Phase 4 | 3 tasks | 2-3 days | Phase 3 complete |
| Phase 5 | 3 tasks | 2-3 days | Phase 4 complete |
| Phase 6 | 3 tasks | 2-3 days | Phase 5 complete |
| **Total** | **18 tasks** | **14-20 days** | Sequential phases |

**Note:** Estimates assume single developer working full-time. Tasks within a phase can be parallelized if multiple developers available.

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Specification Master | Initial task breakdown based on SPEC.md |

---

**End of Tasks Document**
