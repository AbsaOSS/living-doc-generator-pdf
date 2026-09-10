# Input Schema Artifacts

This directory contains the JSON Schemas for the built-in document types.

- The `technical-project` document type is **validated by default**: a run with
  no `schema-path` validates the source against
  `generator-ready-v1.0.0-schema.json`. A raw collector file (no normalized
  `meta`/`content` envelope) fails with a message pointing at the
  `living-doc-toolkit` normalization step.
- Every other schema is **opt-in**: validation runs only when the caller passes a
  `schema-path` input. Without it, the JSON is rendered as-is.

## Schema Files

- **`generator-ready-v1.0.0-schema.json`** — canonical normalized document
  (`document-type: technical-project`); the default validation target.
- **`doc-issues-v1.0.0-schema.json`** — raw collector User Stories source.
- **`ui-tests-v1.0.0-schema.json`** — UI test catalog (`document-type: ui-test-catalog`).
- **`coverage-matrix-v1.0.0-schema.json`** — Coverage matrix (`document-type: coverage-matrix`).

All schemas are JSON Schema Draft-07.

## Vendored `generator-ready-v1.0.0-schema.json`

`generator-ready-v1.0.0-schema.json` is a **verbatim copy** of the file generated
by `living-doc-toolkit`. Do not hand-edit it; re-vendor it from upstream instead.

| Field | Value |
|---|---|
| Source repo | `AbsaOSS/living-doc-toolkit` |
| Path | `packages/datasets_generator_ready/schemas/generator-ready-v1.0.0-schema.json` |
| Pinned commit | `299046c1760a337cf7c8a06d5da5ac7b06ebc2f5` |

Re-vendor with:

```bash
curl -sL -o generator/schemas/generator-ready-v1.0.0-schema.json \
  https://raw.githubusercontent.com/AbsaOSS/living-doc-toolkit/<commit>/packages/datasets_generator_ready/schemas/generator-ready-v1.0.0-schema.json
```

## Usage

Pass the schema path alongside the source file to enable validation:

```yaml
- uses: absaoss/living-doc-generator-pdf@v1
  with:
    source-path: generator-ready.json
    document-type: technical-project
    # schema-path is optional here — technical-project validates against
    # generator-ready-v1.0.0-schema.json by default.
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
