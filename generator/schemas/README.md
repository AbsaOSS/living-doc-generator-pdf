# Input Schema Artifacts

This directory contains the optional JSON Schemas for the three built-in document
types. Schemas are **opt-in**: validation runs only when the caller passes a
`schema-path` input. Without it, the JSON is rendered as-is.

## Schema Files

- **`doc-issues-v1.0.0-schema.json`** — User Stories source (`document-type: user-stories`).
- **`ui-tests-v1.0.0-schema.json`** — UI test catalog (`document-type: ui-test-catalog`).
- **`coverage-matrix-v1.0.0-schema.json`** — Coverage matrix (`document-type: coverage-matrix`).

All schemas are JSON Schema Draft-07.

## Usage

Pass the schema path alongside the source file to enable validation:

```yaml
- uses: absaoss/living-doc-generator-pdf@v1
  with:
    source-path: doc-source.json
    document-type: user-stories
    schema-path: generator/schemas/doc-issues-v1.0.0-schema.json
```

Validate manually with `jsonschema`:

```bash
python -c "
import json, jsonschema
schema = json.load(open('generator/schemas/doc-issues-v1.0.0-schema.json'))
data = json.load(open('doc-source.json'))
jsonschema.validate(data, schema)
print('Validation passed!')
"
```

Or with `ajv-cli`:

```bash
ajv validate -s generator/schemas/doc-issues-v1.0.0-schema.json -d doc-source.json
```

## Versioning

Schema versions are independent of the package version. Bump the file name
(`*-v1.0.0-schema.json`) when the input contract changes and keep older versions
available for downstream producers during migration.
