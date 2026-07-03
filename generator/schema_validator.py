#
# Copyright 2023 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Source JSON loading and optional schema validation."""

import json
import logging
import os
from typing import Any, Optional

import jsonschema
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Exception raised when schema validation fails (exit code 2)."""


def load_source(source_path: str, schema_path: Optional[str] = None) -> dict[str, Any]:
    """Load a JSON source file and optionally validate it against a schema.

    Validation is decoupled from loading: when ``schema_path`` is omitted the
    file is parsed and returned without structural validation.

    Args:
        source_path: Path to the JSON source file to load.
        schema_path: Optional path to a JSON Schema file used for validation.

    Returns:
        Parsed JSON data as a dictionary.

    Raises:
        ValueError: When the file is missing or contains invalid JSON (exit code 1).
        SchemaValidationError: When schema validation fails (exit code 2).
    """
    data = _load_json(source_path)

    if schema_path:
        _validate_against_schema(data, schema_path, source_path)
    else:
        logger.info("No schema-path provided; skipping validation for '%s'.", source_path)

    return data


def _load_json(file_path: str) -> dict[str, Any]:
    """Load and parse a JSON file, raising ValueError on failure."""
    if not os.path.exists(file_path):
        logger.error("File '%s' not found.", file_path)
        raise ValueError(f"Invalid input: File '{file_path}' not found. Ensure source-path points to a valid file.")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            logger.error("Invalid JSON structure in '%s': expected object, got %s", file_path, type(data).__name__)
            raise ValueError(
                f"Invalid input: File '{file_path}' must contain a JSON object (not an array or scalar). "
                f"Ensure the file is valid JSON with a top-level object."
            )
        
        return data
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in '%s': %s", file_path, str(e))
        raise ValueError(
            f"Invalid input: File '{file_path}' contains invalid JSON at line {e.lineno}, column {e.colno}. "
            f"Ensure the file is valid JSON."
        ) from e


def _validate_against_schema(data: dict[str, Any], schema_path: str, source_path: str) -> None:
    """Validate ``data`` against the schema at ``schema_path``."""
    if not os.path.exists(schema_path):
        logger.error("Schema file '%s' not found.", schema_path)
        raise ValueError(f"Invalid input: Schema file '{schema_path}' not found. Ensure schema-path is correct.")

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in schema '%s': %s", schema_path, str(e))
        raise ValueError(f"Invalid input: Schema file '{schema_path}' contains invalid JSON.") from e

    validator = Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(data))

    if errors:
        error_messages = _format_validation_errors(errors)
        full_message = f"Schema validation failed: {error_messages}."
        logger.error(full_message)
        raise SchemaValidationError(full_message)

    logger.info("Schema validation successful for '%s'.", source_path)


def _format_validation_errors(errors: list[jsonschema.ValidationError]) -> str:
    """Format validation errors into a human-readable message.

    Args:
        errors: List of validation errors from jsonschema

    Returns:
        Formatted error message with guidance
    """
    if not errors:
        return "Unknown validation error"

    error = errors[0]
    path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"

    handlers = {
        "required": _format_required_error,
        "const": _format_const_error,
        "format": _format_format_error,
        "type": _format_type_error,
        "minLength": _format_string_error,
        "pattern": _format_pattern_error,
        "minItems": _format_array_error,
        "minimum": _format_minimum_error,
    }

    handler = handlers.get(str(error.validator))
    if handler:
        result = handler(error, path)
        if result:
            return result

    return f"{error.message} at {path}"


def _format_required_error(error: jsonschema.ValidationError, path: str) -> str:
    """Format a 'required' validator error."""
    missing_field = error.message.split("'")[1] if "'" in error.message else "unknown"
    return f"Missing required field '{missing_field}' at {path}"


def _format_const_error(error: jsonschema.ValidationError, path: str) -> str | None:
    """Format a 'const' validator error for schema_version."""
    if "schema_version" in path or (error.absolute_path and error.absolute_path[-1] == "schema_version"):
        return f"Invalid schema_version: expected '1.0', got '{error.instance}'"
    return None


def _format_format_error(error: jsonschema.ValidationError, path: str) -> str | None:
    """Format a 'format' validator error."""
    format_messages = {
        "date-time": f"'{path}' is not a valid ISO 8601 timestamp. Use format: YYYY-MM-DDTHH:MM:SSZ",
        "uri": f"'{path}' is not a valid URL. Use format: http:// or https://",
    }
    return format_messages.get(str(error.validator_value))


def _format_type_error(error: jsonschema.ValidationError, path: str) -> str:
    """Format a 'type' validator error."""
    return f"'{path}' must be of type {error.validator_value}, got {type(error.instance).__name__}"


def _format_string_error(_error: jsonschema.ValidationError, path: str) -> str:
    """Format a 'minLength' validator error."""
    return f"'{path}' must be a non-empty string"


def _format_pattern_error(error: jsonschema.ValidationError, path: str) -> str:
    """Format a 'pattern' validator error."""
    pattern = str(error.validator_value)
    if "\\S" in pattern:
        return f"'{path}' must be a non-empty string"
    if "https?://" in pattern:
        return f"'{path}' is not a valid URL. Use format: http:// or https://"
    return f"'{path}' does not match required pattern"


def _format_array_error(_error: jsonschema.ValidationError, path: str) -> str:
    """Format a 'minItems' validator error."""
    return f"'{path}' must be a non-empty array"


def _format_minimum_error(error: jsonschema.ValidationError, path: str) -> str:
    """Format a 'minimum' validator error."""
    return f"'{path}' must be >= {error.validator_value}, got {error.instance}"
