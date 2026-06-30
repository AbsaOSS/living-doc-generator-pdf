# Input Schema Artifacts

This directory contains the exported JSON Schema for the input contract.

## Schema File

- **`pdf_ready_v1.0-schema.json`** — JSON Schema for pdf_ready.json input data (schema version 1.0)

## How to Generate

From the repository root:

```bash
# Generate and save to default location (this directory)
python -m generator.schema_export

# Or specify a custom output location
python -m generator.schema_export /path/to/custom-schema.json
```

## Usage

Upstream producers (e.g., living-doc-toolkit adapters):
1. Obtain the published schema from this directory
2. Use it in their validation pipeline
3. Validate pdf_ready.json output against the schema

Example with `ajv-cli`:

```bash
ajv validate -s pdf_ready_v1.0-schema.json -d /path/to/pdf_ready.json
```

Example with `jsonschema`:

```bash
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

## Schema Updates

When Pydantic models change:

1. Pydantic models in `generator/models.py` are updated
2. Run `python -m generator.schema_export` to regenerate
3. New versioned file is created: `pdf_ready_v{VERSION}-schema.json`
4. Commit updated schema
5. Release as new version
6. Upstream producers obtain and use updated schema

See `SCHEMA_SYNC.md` for complete synchronization workflow.

## Schema Versioning

The schema version is independent of the package version:

- **Schema Version:** `1.0` (from `get_schema_version()`)
- **Package Version:** See `pyproject.toml`

To change schema version, update `get_schema_version()` in `generator/schema_export.py`.

## Integration

This schema is the authoritative contract between:

- **This repository** (schema producer / data consumer) — consumes pdf_ready.json
- **Upstream producers** (schema consumer / data producer) — validate and produce pdf_ready.json

The pattern ensures:
- Single source of truth: Pydantic models in `generator/models.py`
- No code dependencies between repos
- Schema versioning is explicit and independent
- Validation remains consistent across systems
