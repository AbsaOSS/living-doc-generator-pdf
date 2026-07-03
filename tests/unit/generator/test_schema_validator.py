import json

import pytest

from generator.schema_validator import SchemaValidationError, load_source


@pytest.fixture
def source_file(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps({"items": [{"id": "US-1"}]}), encoding="utf-8")
    return str(path)


@pytest.fixture
def schema_file(tmp_path):
    schema = {
        "type": "object",
        "required": ["items"],
        "properties": {"items": {"type": "array"}},
    }
    path = tmp_path / "schema.json"
    path.write_text(json.dumps(schema), encoding="utf-8")
    return str(path)


def test_load_source_without_schema(source_file) -> None:
    """load_source parses JSON and skips validation when no schema is given."""
    data = load_source(source_file)
    assert data == {"items": [{"id": "US-1"}]}


def test_load_source_missing_file_raises() -> None:
    """load_source raises ValueError when the file is missing."""
    with pytest.raises(ValueError, match="not found"):
        load_source("/nonexistent/data.json")


def test_load_source_invalid_json_raises(tmp_path) -> None:
    """load_source raises ValueError on invalid JSON."""
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON"):
        load_source(str(path))


def test_load_source_with_valid_schema(source_file, schema_file) -> None:
    """load_source validates successfully against a matching schema."""
    data = load_source(source_file, schema_file)
    assert data["items"][0]["id"] == "US-1"


def test_load_source_schema_validation_failure(tmp_path, schema_file) -> None:
    """load_source raises SchemaValidationError when data violates the schema."""
    path = tmp_path / "data.json"
    path.write_text(json.dumps({"not_items": []}), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="Schema validation failed"):
        load_source(str(path), schema_file)


def test_load_source_missing_schema_file_raises(source_file) -> None:
    """load_source raises ValueError when the schema file is missing."""
    with pytest.raises(ValueError, match="Schema file"):
        load_source(source_file, "/nonexistent/schema.json")


def test_load_source_invalid_schema_json_raises(source_file, tmp_path) -> None:
    """load_source raises ValueError when the schema file is invalid JSON."""
    bad_schema = tmp_path / "bad_schema.json"
    bad_schema.write_text("{not json", encoding="utf-8")

    with pytest.raises(ValueError, match="Schema file"):
        load_source(source_file, str(bad_schema))
