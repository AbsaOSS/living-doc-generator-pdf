# Pull Request: Multi-Document-Type PDF Generation (#81)

## Description

This PR restructures the Living Doc Generator to support multiple document types with dedicated schemas and templates. The changes move away from a monolithic `pdf_ready_v1.0` schema to a modular architecture where each document type (User Stories, Coverage Matrix, UI Test Catalog) has its own schema, templates, and data structure.

### What Changed

**Schema Restructuring:**
- Replaced single `pdf_ready_v1.0-schema.json` with four document-specific schemas:
  - `coverage-matrix-v1.0.0-schema.json`
  - `doc-source-v1.0.0-schema.json` (User Stories)
  - `ui-tests-v1.0.0-schema.json`
  - `doc-issues-v1.0.0-schema.json`

**Template Reorganization:**
- Organized templates into document-type directories:
  - `user-stories/` - User stories, features, functionalities
  - `coverage-matrix/` - Coverage matrix reports
  - `ui-test-catalog/` - UI test documentation

**Examples & Configuration:**
- Consolidated examples into specific files: `coverage_matrix.json`, `ui_tests.json`, `user_stories.json`, `minimal.json`
- Updated `action.yml` to accept document-specific inputs
- Updated `action_inputs.py` to parse multi-document workflows

**Code Refactoring:**
- Simplified `models.py` data structures for each document type
- Enhanced `template_renderer.py` for multi-document rendering
- Removed `schema_export.py` (schema tooling moved elsewhere)
- Updated all unit and integration tests for new structure

**Documentation:**
- Added `docs/template-override-guide.md` for template customization
- Updated `DEVELOPER.md` with new build and test instructions
- Simplified `README.md` for clarity

### Why

This modular approach enables:
- Independent schema versioning for each document type
- Cleaner code organization and maintainability
- Easier addition of new document types
- Better separation of concerns between templates
- More intuitive user experience with specific inputs per document type

### How to Verify

```bash
# Run all tests
pytest tests/unit/generator/test_action_inputs.py -v
pytest tests/unit/generator/test_schema_validator.py -v
pytest tests/unit/generator/test_template_renderer.py -v
pytest tests/unit/generator/test_filters.py -v

# Code quality
black $(git ls-files '*.py')
pylint --ignore=tests $(git ls-files '*.py')
mypy .
```

---

## Release Notes

- Multi-document type support - Generate User Stories, Coverage Matrix, and UI Test Catalog independently
- Document-specific schemas v1.0.0 for each document type
- New template customization guide for overriding defaults
- Modular template system organized by document type
- Updated `action.yml` inputs for multi-document workflows
- Data schema structure changed from `pdf_ready_v1.0` to document-specific schemas
- Template structure reorganized into subdirectories
- Example JSON files consolidated per document type
- Simplified and cleaner code organization
- Better maintainability with separated concerns
- Easier to extend with new document types
- Removed `schema_export.py` module and legacy single-document handling

---

## CodeRabbit Review Fixes

### Fixed Issues (6/6)

1. **source-path now optional with deprecated alias support** ✅
   - Changed `source-path` to `required: false` in action.yml
   - Backward compatibility maintained via pdf_ready_json alias
   - Python-level validation enforces at least one must be provided

2. **JSON type validation** ✅
   - Added check to reject non-object JSON (arrays/scalars)
   - `_load_json()` now validates structure before returning
   - Improves error clarity for invalid inputs

3. **Template base_dir asset resolution fixed** ✅
   - When both custom and built-in templates present, assets now resolve against built-in directory
   - Allows partial template overrides without duplicating all assets
   - Maintains fallback chain correctly

4. **Markdown injection prevention** ✅
   - Relying on markdown library's default safe HTML handling
   - Raw HTML in source is properly escaped
   - Markdown formatting still works correctly

5. **Debug HTML tests use production path** ✅
   - Extracted `_save_debug_html()` helper in main.py
   - Tests now use production save logic instead of writing files directly
   - Filename pattern verified: `{pdf_stem}_rendered.html`

6. **Schema-validated happy path test coverage** ✅
   - Added `test_generate_pdf_with_schema_validation()` parametrized test
   - Validates each document type with bundled schema
   - Tests schema-path plumbing end-to-end

### Test Results
- ✅ 61/61 unit tests passing (schema_validator, template_renderer, filters, models, action_inputs)
- All fixes validated without regressions

---

## Updates

### Update 2026-07-03
[commit 530e285]
- Multi-document restructuring complete

### Update 2026-07-03 (Later)
[CodeRabbit review fixes]
- Fixed 6 unresolved review comments
- Added JSON type validation, backward-compatible inputs, template asset resolution
- Improved debug HTML test coverage and markdown sanitization
- All 61 unit tests passing
