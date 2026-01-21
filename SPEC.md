# Living Documentation PDF Generator - System Specification

**Version:** 1.0
**Last Updated:** 2026-01-21
**Status:** Active

---

## 1. Overview & Scope

### 1.1 Purpose

The Living Documentation PDF Generator is a source-agnostic GitHub Action that consumes a **canonical JSON format** (`pdf_ready.json`) and produces professional PDF documentation using Jinja templates and WeasyPrint.

### 1.2 Scope

**In Scope:**
- Consuming `pdf_ready.json` (canonical, PDF-ready JSON)
- Rendering HTML using Jinja2 templates
- Converting HTML to PDF using WeasyPrint
- Providing default Living Doc template pack
- Supporting user-provided template overrides
- Generating debug artifacts (rendered HTML, PDF report)
- Clear error handling and validation

**Out of Scope:**
- Source data collection (handled by `living-doc-collector-gh`)
- Data normalization and enrichment (handled by Builder repository)
- Content parsing or extraction (AST, Markdown parsing)
- Analytics or "smart" content generation (coverage matrices, statistics)
- Source detection (GitHub vs Azure DevOps)

### 1.3 Design Principles

1. **Source Independence**: No knowledge of GitHub, Azure DevOps, or other sources
2. **Logic-Free Rendering**: All intelligence resides in the canonical JSON schema
3. **Template-Driven**: Behavior controlled via Jinja templates, not code
4. **Fail-Fast**: Clear, actionable error messages for invalid inputs
5. **Deterministic**: Same input always produces same output

---

## 2. Glossary & Invariants

### 2.1 Key Terms

- **pdf_ready.json**: Canonical JSON format containing all data needed for PDF generation
- **Template Pack**: Collection of Jinja templates, CSS, fonts, and assets
- **Canonical Schema**: Well-defined JSON structure (version 1.0) consumed by this action
- **User Story**: Normalized documentation unit within `pdf_ready.json`
- **WeasyPrint**: HTML-to-PDF rendering engine used by this action

### 2.2 Invariants

1. **Schema Version Stability**: Schema version 1.0 fields never change meaning
2. **Template Isolation**: Templates depend only on canonical schema, not implementation details
3. **Reproducibility**: Given identical inputs, outputs are byte-identical (timestamps excluded)
4. **Asset Resolution**: All assets (fonts, images, CSS) resolve correctly in CI environments
5. **Error Determinism**: Same invalid input produces same error message and exit code

---

## 3. Interfaces & Contracts

### 3.1 GitHub Action Interface

#### 3.1.1 Action Inputs

| Input Name | Type | Required | Default | Description |
|------------|------|----------|---------|-------------|
| `pdf_ready_json` | string (path) | **Yes** | - | Path to pdf_ready.json file |
| `output_path` | string (path) | No | `output.pdf` | Path for generated PDF file |
| `template_dir` | string (path) | No | _(built-in)_ | Directory containing custom Jinja templates |
| `debug_html` | boolean | No | `false` | Save intermediate HTML as `rendered.html` |
| `verbose` | boolean | No | `false` | Enable verbose logging |

**Input Validation Rules:**
- `pdf_ready_json`: Must be a valid file path; file must exist and be readable
- `output_path`: Must be a valid path; parent directory created if missing
- `template_dir`: If provided, must be a valid directory path; directory must exist
- `debug_html`: Accepts `true`, `false`, `1`, `0`, `yes`, `no` (case-insensitive)
- `verbose`: Accepts `true`, `false`, `1`, `0`, `yes`, `no` (case-insensitive)

#### 3.1.2 Action Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `pdf_path` | string (path) | Absolute path to generated PDF file |
| `html_path` | string (path) | Absolute path to debug HTML (if `debug_html=true`) |
| `report_path` | string (path) | Absolute path to `pdf_report.json` |

#### 3.1.3 Exit Codes

| Exit Code | Condition | Error Message Prefix |
|-----------|-----------|---------------------|
| 0 | Success | - |
| 1 | Invalid input (missing file, invalid JSON) | `Invalid input:` |
| 2 | Schema validation failure | `Schema validation failed:` |
| 3 | Template error (missing, invalid) | `Template error:` |
| 4 | Rendering error (WeasyPrint failure) | `Rendering failed:` |
| 5 | File I/O error (write failure) | `File I/O error:` |

**Error Message Format:**
```
{prefix} {specific_detail}. {actionable_guidance}
```

**Examples:**
```
Invalid input: File 'data.json' not found. Ensure pdf_ready_json points to a valid file.
Schema validation failed: Missing required field 'schema_version'. Ensure JSON follows canonical schema v1.0.
Template error: Template 'main.html.jinja' not found. Check template_dir path or use default templates.
Rendering failed: WeasyPrint could not load font 'Arial.ttf'. Verify font files are present in assets directory.
```

### 3.2 PDF-Ready JSON Schema (v1.0)

#### 3.2.1 Schema Version

**Field:** `schema_version`
**Type:** String
**Required:** Yes
**Allowed Values:** `"1.0"`
**Validation:** Must be exactly `"1.0"`

#### 3.2.2 Metadata Section

**Field:** `meta`
**Type:** Object
**Required:** Yes

**Required Fields:**
```json
{
  "document_title": "string (non-empty)",
  "document_version": "string (non-empty, semver recommended)",
  "generated_at": "ISO 8601 UTC timestamp",
  "source_set": ["array of source identifiers"],
  "selection_summary": {
    "total_items": "integer >= 0",
    "included_items": "integer >= 0",
    "excluded_items": "integer >= 0"
  }
}
```

**Optional Fields:**
```json
{
  "run_context": {
    "ci_run_id": "string",
    "triggered_by": "string",
    "branch": "string",
    "commit_sha": "string"
  }
}
```

**Validation Rules:**
- `document_title`: 1-200 characters, non-empty after trimming
- `document_version`: 1-50 characters, semver format recommended
- `generated_at`: Must be valid ISO 8601 format with timezone
- `source_set`: Non-empty array, each element is a non-empty string
- `selection_summary.total_items`: Must equal `included_items + excluded_items`

#### 3.2.3 Content Section

**Field:** `content`
**Type:** Object
**Required:** Yes

**Required Fields:**
```json
{
  "user_stories": [
    {
      "id": "string (canonical stable ID)",
      "title": "string (non-empty)",
      "state": "string (e.g., 'open', 'closed')",
      "tags": ["array of strings"],
      "url": "string (valid URL)",
      "timestamps": {
        "created": "ISO 8601 timestamp",
        "updated": "ISO 8601 timestamp"
      },
      "sections": {
        "description": "string (Markdown)",
        "business_value": "string (Markdown, optional)",
        "preconditions": "string (Markdown, optional)",
        "acceptance_criteria": "string (Markdown, optional)",
        "user_guide": "string (Markdown, optional)",
        "connections": "string (Markdown, optional)",
        "last_edited": "string (Markdown, optional)"
      }
    }
  ]
}
```

**Optional Fields:**
```json
{
  "overview": {
    "summary_stats": {},
    "index_tables": []
  },
  "coverage_matrix": {
    "version": "string",
    "matrix_data": []
  }
}
```

**Validation Rules:**
- `user_stories`: Array with 0+ elements (empty array is valid)
- `id`: Unique within the array, 1-200 characters
- `title`: 1-500 characters, non-empty after trimming
- `state`: Non-empty string, typically `open` or `closed`
- `tags`: Array (can be empty)
- `url`: Must be a valid URL format (http/https)
- `timestamps.created`: Must be valid ISO 8601
- `timestamps.updated`: Must be valid ISO 8601, >= `created`
- `sections`: All fields are optional strings; missing sections represented as `null` or empty string

#### 3.2.4 Complete Example

```json
{
  "schema_version": "1.0",
  "meta": {
    "document_title": "Product Requirements - Release 2.1",
    "document_version": "2.1.0",
    "generated_at": "2026-01-21T12:00:00Z",
    "source_set": ["github:AbsaOSS/living-doc-generator-pdf"],
    "selection_summary": {
      "total_items": 15,
      "included_items": 12,
      "excluded_items": 3
    },
    "run_context": {
      "ci_run_id": "123456",
      "triggered_by": "user@example.com",
      "branch": "main",
      "commit_sha": "abc123def456"
    }
  },
  "content": {
    "user_stories": [
      {
        "id": "github:AbsaOSS/project#42",
        "title": "User login with SSO",
        "state": "open",
        "tags": ["authentication", "priority:high"],
        "url": "https://github.com/AbsaOSS/project/issues/42",
        "timestamps": {
          "created": "2026-01-10T08:00:00Z",
          "updated": "2026-01-20T14:30:00Z"
        },
        "sections": {
          "description": "As a user, I want to log in using SSO...",
          "business_value": "Reduces friction for enterprise users",
          "preconditions": "SSO provider configured",
          "acceptance_criteria": "- User can click SSO button\n- Redirect to provider\n- Return with session",
          "user_guide": null,
          "connections": "Related to #41, #43",
          "last_edited": "Updated by alice@example.com on 2026-01-20"
        }
      }
    ]
  }
}
```

### 3.3 PDF Report JSON Schema

**File:** `pdf_report.json`
**Purpose:** Diagnostics and metadata about the PDF generation process

**Required Fields:**
```json
{
  "schema_version": "1.0",
  "generated_at": "ISO 8601 timestamp",
  "input_file": "path to pdf_ready.json",
  "output_file": "path to generated PDF",
  "template_pack": {
    "type": "built-in | custom",
    "path": "template directory path or 'built-in'"
  },
  "statistics": {
    "user_story_count": "integer",
    "total_pages": "integer (if determinable)",
    "file_size_bytes": "integer"
  },
  "errors": [],
  "warnings": []
}
```

**Error/Warning Format:**
```json
{
  "level": "error | warning",
  "message": "Human-readable message",
  "context": "Additional context (optional)"
}
```

**Example:**
```json
{
  "schema_version": "1.0",
  "generated_at": "2026-01-21T12:05:00Z",
  "input_file": "/workspace/pdf_ready.json",
  "output_file": "/workspace/output.pdf",
  "template_pack": {
    "type": "built-in",
    "path": "built-in"
  },
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

### 3.4 Template Pack Structure

#### 3.4.1 Built-in Template Pack

**Location:** `generator/templates/` (within repository)

**Required Files:**
- `main.html.jinja` - Main document template
- `styles.css` - Document styling
- `cover.html.jinja` - Cover page template (optional)
- `user_story.html.jinja` - User story block template

**Required Directories:**
- `assets/fonts/` - Font files for WeasyPrint
- `assets/images/` - Logo and image assets

#### 3.4.2 Custom Template Pack

**Structure:** User-provided directory with same layout as built-in

**Override Behavior:**
- If `template_dir` is provided, it takes precedence
- Missing templates fall back to built-in defaults
- CSS files are loaded in order: built-in, then custom (custom overrides)

**Template Variables Available:**

All templates receive the entire `pdf_ready.json` structure:
```jinja
{{ schema_version }}
{{ meta.document_title }}
{{ meta.document_version }}
{{ meta.generated_at }}
{{ content.user_stories }} {# array #}
```

**Filters Available:**
- `markdown` - Convert Markdown to HTML
- `format_datetime` - Format ISO timestamps
- `escape_html` - HTML entity escaping (automatic in Jinja)

### 3.5 Asset Resolution

**Base URL Handling:**
- All asset URLs in templates must be relative to the template directory
- WeasyPrint base_url set to template directory absolute path
- Font paths resolved via `@font-face` declarations in CSS
- Image paths resolved relative to template directory

**Font Loading:**
```css
@font-face {
  font-family: 'DejaVu Sans';
  src: url('assets/fonts/DejaVuSans.ttf');
}
```

**Image Loading:**
```html
<img src="assets/images/logo.png" alt="Logo">
```

---

## 4. Data & Storage Schemas

### 4.1 Input File

**Format:** JSON (UTF-8 encoded)
**Size Limit:** 50 MB (soft limit for CI performance)
**Validation:** JSON schema validation before processing

### 4.2 Output Files

#### 4.2.1 PDF Document

**Format:** PDF/A-1b (archival quality)
**Encoding:** UTF-8 for text content
**Metadata:** Embedded (title, author, creation date)

#### 4.2.2 Debug HTML

**Format:** HTML5
**Purpose:** Intermediate rendering for debugging template issues
**Generated:** Only if `debug_html=true`

#### 4.2.3 PDF Report

**Format:** JSON (UTF-8 encoded)
**Purpose:** Machine-readable diagnostics
**Always Generated:** Yes

---

## 5. Algorithms & Rules

### 5.1 Processing Pipeline

```
1. Load and parse pdf_ready.json
2. Validate against schema v1.0
3. Load template pack (custom or built-in)
4. Render HTML using Jinja2
5. (Optional) Save debug HTML
6. Render PDF using WeasyPrint
7. Generate pdf_report.json
8. Set action outputs
```

### 5.2 Error Handling Strategy

**Fail-Fast Approach:**
- Schema validation errors stop processing immediately
- Template errors stop processing immediately
- Rendering errors stop processing immediately

**Partial Success Not Allowed:**
- Either a complete, valid PDF is produced, or the action fails
- No "best-effort" rendering with missing sections

### 5.3 Determinism

**Guaranteed Deterministic:**
- Same `pdf_ready.json` produces same content structure
- Template rendering is deterministic
- Error messages for same errors are identical

**Non-Deterministic (Acceptable):**
- `generated_at` timestamps in `pdf_report.json`
- PDF metadata timestamps
- File size may vary slightly due to compression

### 5.4 Performance Budgets

| Operation | Target | Maximum |
|-----------|--------|---------|
| JSON parsing | < 1 second | 5 seconds |
| Schema validation | < 2 seconds | 10 seconds |
| Template rendering | < 5 seconds | 30 seconds |
| PDF generation (100 pages) | < 10 seconds | 60 seconds |
| Total action runtime | < 30 seconds | 120 seconds |

**Note:** Budgets assume 100 user stories, ~500 KB JSON, CI environment

---

## 6. Phase-by-Phase Acceptance Criteria

### Phase 1: Core Infrastructure

**Acceptance Criteria:**
- [ ] `pdf_ready.json` schema v1.0 fully defined and documented
- [ ] JSON schema validation implemented with clear error messages
- [ ] Action inputs read from environment variables correctly
- [ ] Exit codes match specification for each error type
- [ ] Basic logging infrastructure in place

**Verification:**
- `tests/unit/test_schema_validation.py` - JSON schema validation tests
- `tests/unit/test_action_inputs.py` - Input parsing tests
- `tests/integration/test_error_codes.py` - Exit code verification

### Phase 2: Template Engine

**Acceptance Criteria:**
- [ ] Jinja2 template rendering functional
- [ ] Built-in template pack created and tested
- [ ] Custom template override mechanism works
- [ ] Markdown filter converts Markdown to HTML correctly
- [ ] Asset resolution (fonts, images) works in CI

**Verification:**
- `tests/unit/test_template_rendering.py` - Template engine tests
- `tests/integration/test_custom_templates.py` - Template override tests
- `verifications/verify_built_in_templates.py` - Template pack verification

### Phase 3: PDF Generation

**Acceptance Criteria:**
- [ ] WeasyPrint integration functional
- [ ] PDF output valid and openable in standard viewers
- [ ] Debug HTML output works when enabled
- [ ] `pdf_report.json` generated with correct schema
- [ ] PDF metadata (title, author) embedded correctly

**Verification:**
- `tests/integration/test_pdf_generation.py` - End-to-end PDF tests
- `verifications/verify_pdf_output.py` - PDF validation script
- `tests/integration/test_debug_html.py` - Debug HTML tests

### Phase 4: Error Handling & Edge Cases

**Acceptance Criteria:**
- [ ] Invalid JSON detected and reported clearly
- [ ] Missing required fields detected with specific error messages
- [ ] Template errors (missing files) handled gracefully
- [ ] Rendering errors (font loading failures) reported clearly
- [ ] Large JSON files (50 MB) handled without crashes

**Verification:**
- `tests/integration/test_error_handling.py` - Error scenario tests
- `tests/integration/test_edge_cases.py` - Edge case coverage
- `verifications/verify_error_messages.py` - Error message consistency check

### Phase 5: GitHub Action Integration

**Acceptance Criteria:**
- [ ] Action runs successfully in GitHub Actions CI
- [ ] Artifacts (PDF, HTML, report) uploaded correctly
- [ ] Action outputs set and consumable by downstream steps
- [ ] Example workflow demonstrates usage
- [ ] Documentation complete (README, examples)

**Verification:**
- `.github/workflows/test.yml` - CI workflow
- `.github/workflows/example.yml` - Example usage workflow
- Manual verification in CI environment

---

## 7. Change Control

### 7.1 Versioned Contracts

**Schema Version 1.0:**
- Field meanings and types are **immutable**
- New optional fields may be added (backwards compatible)
- Breaking changes require new schema version (2.0)

**Action Inputs:**
- Input names and defaults are **stable**
- New optional inputs may be added
- Removing inputs requires major version bump

**Exit Codes:**
- Exit code meanings are **stable**
- New exit codes may be added for new error types
- Changing existing exit code meanings requires major version bump

### 7.2 Approval Requirements

**Changes Requiring Review:**
- Schema modifications (even additions)
- Template pack changes affecting rendering
- Error message text changes
- Exit code changes
- Performance budget changes

**Changes Not Requiring Special Approval:**
- Internal refactoring (preserving behavior)
- Logging improvements
- Documentation updates
- Test additions

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Coverage Target:** ≥ 80%
**Focus:**
- JSON schema validation logic
- Input parsing and validation
- Template rendering (isolated)
- Error message formatting

### 8.2 Integration Tests

**Focus:**
- End-to-end PDF generation
- Custom template overrides
- Asset resolution in CI
- Error handling scenarios
- Large input files

### 8.3 Verification Scripts

**Purpose:** Manual validation and CI quality gates

**Scripts:**
- `verifications/verify_schema_examples.py` - Validate example JSON files
- `verifications/verify_pdf_output.py` - PDF quality checks (metadata, fonts)
- `verifications/verify_error_messages.py` - Error message consistency
- `verifications/verify_templates.py` - Template syntax and completeness

---

## 9. Dependencies

### 9.1 Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `Jinja2` | `^3.1.0` | Template rendering |
| `WeasyPrint` | `^60.0` | HTML to PDF conversion |
| `jsonschema` | `^4.20.0` | JSON schema validation |
| `Markdown` | `^3.5.0` | Markdown to HTML conversion |
| `Pillow` | `^10.0.0` | Image processing (required by WeasyPrint) |

### 9.2 Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | `^9.0.0` | Testing framework |
| `pytest-cov` | `^7.0.0` | Coverage reporting |
| `black` | `^26.0.0` | Code formatting |
| `pylint` | `^4.0.0` | Code quality |
| `mypy` | `^1.19.0` | Type checking |

---

## 10. Security Considerations

### 10.1 Input Validation

- **JSON Injection:** All JSON inputs validated against strict schema
- **Path Traversal:** All file paths validated to prevent directory traversal
- **Template Injection:** Jinja2 autoescape enabled for user-provided content
- **Resource Exhaustion:** File size limits enforced (50 MB JSON)

### 10.2 Asset Handling

- **Font Files:** Only load fonts from controlled directories (built-in or user-specified)
- **Image Files:** Validate image formats before loading
- **External URLs:** No external URL fetching in templates (offline rendering)

### 10.3 Secrets

- **No Secrets in JSON:** `pdf_ready.json` must not contain secrets or credentials
- **No API Calls:** Action does not make network calls (offline operation)

---

## 11. Monitoring & Observability

### 11.1 Logging Levels

| Level | Purpose | Examples |
|-------|---------|----------|
| DEBUG | Detailed diagnostics | Template variable resolution, asset paths |
| INFO | Normal operation | "Processing user story 12/50", "PDF generated successfully" |
| WARNING | Non-fatal issues | "Missing acceptance_criteria for story #42" |
| ERROR | Fatal failures | "JSON schema validation failed", "Template rendering error" |

### 11.2 Metrics (via pdf_report.json)

- User story count processed
- Total pages in PDF
- File size of generated PDF
- Processing time per phase (if performance debugging enabled)
- Warning count (missing sections, etc.)

---

## 12. Future Extensions

### 12.1 Planned Features (Out of Scope for v1.0)

- **Multi-Document Support:** Generate multiple PDFs from single JSON
- **Custom Fonts:** User-provided font packages
- **Internationalization:** Template strings in multiple languages
- **PDF/A-3 Support:** Enhanced archival formats
- **Batch Processing:** Process multiple `pdf_ready.json` files in one action run

### 12.2 Extension Points

- **Template Filters:** Plugin system for custom Jinja filters
- **Post-Processors:** Hook for PDF post-processing (watermarks, signatures)
- **Validators:** Pluggable schema validators for different schema versions

---

## 13. References

### 13.1 Related Specifications

- Living Documentation PDF Pipeline Design (Issue #X)
- PDF-Ready JSON Schema Definition (Section 3.2)
- Builder Repository Specification (external)

### 13.2 External Standards

- [JSON Schema Specification](https://json-schema.org/)
- [Jinja2 Template Language](https://jinja.palletsprojects.com/)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)
- [PDF/A Standard (ISO 19005)](https://www.iso.org/standard/38920.html)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-21 | Specification Master | Initial specification based on design document |

---

**End of Specification**
