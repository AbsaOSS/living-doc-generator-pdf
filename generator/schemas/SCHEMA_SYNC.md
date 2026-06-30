# Schema Synchronization Guide

## Pattern: Pydantic-First (Schema Producer / Data Consumer)

This repository uses the **Pydantic-First** pattern where **this repository** (living-doc-generator-pdf):
- **Consumes data** from upstream living-doc systems (data consumer role)
- **Produces schema** as an artifact for upstream systems to validate against (schema producer role)

The Pydantic models in this repo are the **single source of truth** for the input contract.

```
┌─────────────────────────────────────────────────────────┐
│ Living Doc Generator PDF (This Repo)                    │
│ SCHEMA PRODUCER / DATA CONSUMER                         │
│                                                         │
│ • Pydantic models (generator/models.py) ◄── SOURCE     │
│ • Export JSON Schema (generator/schema_export.py)       │
│ • Save to: generator/schemas/pdf_ready_v1.0-schema.json│
│ • Publish schema as artifact                           │
└─────────────────────────────────────────────────────────┘
                      │
                      │ Schema published as independent artifact
                      │ (no direct code dependency)
                      ▼
┌─────────────────────────────────────────────────────────┐
│ Upstream Producers (Independent)                        │
│ SCHEMA CONSUMER / DATA PRODUCER                         │
│                                                         │
│ • Obtain published schema                              │
│ • Use it independently for validation                  │
│ • Publish validated pdf_ready.json to this repo        │
└─────────────────────────────────────────────────────────┘
```

**Key:** No direct code dependency. The schema is a published artifact that each
repo uses independently within their own validation pipeline.

## Schema Version

- **Input Schema Version:** `1.0` (independent of package version)
- **Package Version:** See `pyproject.toml`
- **Producer Compatibility Range:** `>=1.0,<2.0` (implicit)

## Workflow: When Pydantic Models Change

### 1. Consumer (This Repo) Updates Model

Edit [generator/models.py](generator/models.py):

```python
class UserStory(BaseModel):
    """Represents a single user story in the documentation."""

    id: str = Field(min_length=1, max_length=200, description="...")
    title: str = Field(min_length=1, max_length=500, description="...")
    # ... add new field
    custom_field: Optional[str] = Field(default=None, description="...")
```

### 2. Export Updated Schema

Schema is automatically saved with version in filename:

```bash
# From repository root
python -m generator.schema_export

# Schema is now in: generator/schemas/pdf_ready_v1.0-schema.json

# Or programmatically:
from generator.schema_export import export_schema, get_schema_version
schema = export_schema()  # Saved to default location with version
print(f"Schema version: {get_schema_version()}")  # 1.0
```

Or save to custom location:

```bash
python -m generator.schema_export /path/to/custom-schema.json
```

### 3. Validate Tests Pass

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests
pytest tests/
```

### 4. Commit & Publish Schema as Artifact

Schema changes are committed and published with version in filename:

```bash
# Commit the updated schema (versioned filename)
git add generator/schemas/pdf_ready_v1.0-schema.json
git commit -m "feat: update input schema to v1.0

- Added custom_field to UserStory model
- See SCHEMA_SYNC.md for details"

# Create release with schema as artifact
# Schema will be available at: 
# https://github.com/AbsaOSS/living-doc-generator-pdf/blob/main/generator/schemas/pdf_ready_v1.0-schema.json
```

Schema is now available for downstream consumers.

### 5. Upstream Producers Obtain & Use Schema

Producers (e.g., living-doc-toolkit adapters):
- Obtain published schema (from GitHub, documentation, releases, etc.)
- Integrate into their validation pipeline
- Use to validate pdf_ready.json output
- **No direct code dependency** on this repo

Example upstream workflow:

```yaml
# .github/workflows/generate-pdf-ready.yml
- name: Download schema
  run: |
    curl -O https://raw.githubusercontent.com/AbsaOSS/living-doc-generator-pdf/main/generator/schemas/pdf_ready_v1.0-schema.json

- name: Validate output against schema
  run: |
    python -c "
    import json
    import jsonschema
    
    with open('pdf_ready_v1.0-schema.json') as f:
        schema = json.load(f)
    
    with open('pdf_ready.json') as f:
        data = json.load(f)
    
    jsonschema.validate(data, schema)
    print('Validation passed!')
    "
```

## Workflow: When Producer Version Increments

If this repo releases `v1.1.0` with schema changes:

1. **Upstream producers download release notes**
2. **Identify breaking vs. non-breaking changes**
3. **If breaking:**
   - Schema version changes (e.g., from `1.0` to `2.0`)
   - Update filename: `pdf_ready_v2.0-schema.json`
   - Update `get_schema_version()` in `generator/schema_export.py`
   - Document in release notes

4. **If non-breaking:**
   - Schema version stays same (e.g., `1.0`)
   - Upstream producers can continue using existing validation
   - Graceful degradation for older producers

## File Locations

| File | Purpose |
|------|---------|
| [generator/models.py](generator/models.py) | Pydantic models (source of truth) |
| [generator/schema_export.py](generator/schema_export.py) | Export models to JSON Schema |
| [generator/schemas/README.md](generator/schemas/README.md) | Schema directory documentation |
| [generator/schema_validator.py](generator/schema_validator.py) | Validation using jsonschema |

## Example: Adding a New Field

**Step 1:** Update model

```python
# generator/models.py
class UserStory(BaseModel):
    """..."""
    # ... existing fields
    priority: Optional[str] = Field(default=None, description="Optional priority level")
```

**Step 2:** Export schema

```bash
python -m generator.schema_export
```

**Step 3:** Verify schema was updated

```bash
grep -A 5 '"priority"' generator/schemas/pdf_ready_v1.0-schema.json
```

**Step 4:** Commit

```bash
git add generator/models.py generator/schemas/pdf_ready_v1.0-schema.json
git commit -m "feat: add priority field to UserStory"
```

**Step 5:** Upstream producers update

Upstream systems will see the new schema in next release and can:
- Add validation for priority field
- Handle older data gracefully (since it's optional)

## Example: Breaking Change

**Step 1:** Update model with breaking change

```python
# generator/models.py - make field required
class UserStory(BaseModel):
    """..."""
    # Change from Optional[str] to str
    priority: str = Field(description="Priority level (required)")
```

**Step 2:** Update schema version

```python
# generator/schema_export.py
def get_schema_version() -> str:
    return "2.0"  # Changed from "1.0"
```

**Step 3:** Export schema

```bash
python -m generator.schema_export
# Creates: generator/schemas/pdf_ready_v2.0-schema.json
```

**Step 4:** Commit with release

```bash
git add generator/models.py generator/schema_export.py generator/schemas/pdf_ready_v2.0-schema.json
git commit -m "feat!: require priority field on UserStory

BREAKING CHANGE: priority field is now required.
Upstream producers must provide this field.
See SCHEMA_SYNC.md for migration guide."

# Tag for release
git tag -a v2.0.0 -m "Schema v2.0 - breaking changes"
```

**Step 5:** Upstream producers respond

Upstream systems see breaking change and:
- Update their code to provide priority field
- Update validation to use new schema v2.0
- Test compatibility before deploying

## Best Practices

1. **Schema versioning is explicit:** Use `get_schema_version()` in one place
2. **Versions are independent:** Schema version ≠ package version
3. **Backward compatibility:** Prefer optional fields when possible
4. **Document changes:** Include migration guides for breaking changes
5. **Test schema:** Validate test fixtures against exported schema
6. **Publish schema:** Include in releases, documentation, and GitHub artifacts

## References

- [Pydantic documentation](https://docs.pydantic.dev/)
- [JSON Schema specification](https://json-schema.org/)
- [SCHEMA_SYNC.md](SCHEMA_SYNC.md) — This file
- [generator/models.py](generator/models.py) — Model definitions
- [generator/schema_export.py](generator/schema_export.py) — Export logic
- [generator/schemas/README.md](generator/schemas/README.md) — Usage guide
