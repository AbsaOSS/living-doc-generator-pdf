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

"""Schema validation for pdf_ready.json files."""

import json
import logging
import os
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Exception raised when schema validation fails (exit code 2)."""


def validate_pdf_ready_json(file_path: str) -> dict[str, Any]:
    """Validate pdf_ready.json against schema v1.0 and return parsed data.

    Args:
        file_path: Path to the pdf_ready.json file to validate

    Returns:
        Parsed JSON data as a dictionary

    Raises:
        ValueError: When file is missing or contains invalid JSON (exit code 1)
        SchemaValidationError: When schema validation fails (exit code 2)
    """
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error("File '%s' not found.", file_path)
        raise ValueError(f"Invalid input: File '{file_path}' not found. Ensure pdf_ready_json points to a valid file.")

    # Load and parse JSON
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in '%s': %s", file_path, str(e))
        raise ValueError(
            f"Invalid input: File '{file_path}' contains invalid JSON at line {e.lineno}, column {e.colno}. "
            f"Ensure the file is valid JSON."
        ) from e

    # Load the schema
    schema_path = Path(__file__).parent / "schemas" / "pdf_ready_v1.0.json"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Failed to load schema file: %s", str(e))
        raise RuntimeError(f"Internal error: Schema file not found or invalid. {str(e)}") from e

    # Validate against schema
    validator = Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(data))

    if errors:
        # Format error messages
        error_messages = _format_validation_errors(errors)
        full_message = f"Schema validation failed: {error_messages}. Ensure JSON follows canonical schema v1.0."
        logger.error(full_message)
        raise SchemaValidationError(full_message)

    logger.info("Schema validation successful for '%s'.", file_path)
    return data


def _format_validation_errors(errors: list[jsonschema.ValidationError]) -> str:
    """Format validation errors into a human-readable message.

    Args:
        errors: List of validation errors from jsonschema

    Returns:
        Formatted error message with guidance
    """
    # Prioritize the first error for clarity
    if not errors:
        return "Unknown validation error"

    error = errors[0]
    path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"

    # Handle specific error types with actionable guidance
    message = None

    if error.validator == "required":
        missing_field = error.message.split("'")[1] if "'" in error.message else "unknown"
        message = f"Missing required field '{missing_field}' at {path}"
    elif error.validator == "const" and (
        "schema_version" in path or (error.absolute_path and error.absolute_path[-1] == "schema_version")
    ):
        message = f"Invalid schema_version: expected '1.0', got '{error.instance}'"
    elif error.validator == "format":
        if error.validator_value == "date-time":
            message = f"'{path}' is not a valid ISO 8601 timestamp. Use format: YYYY-MM-DDTHH:MM:SSZ"
        elif error.validator_value == "uri":
            message = f"'{path}' is not a valid URL. Use format: http:// or https://"
    elif error.validator == "type":
        expected = error.validator_value
        actual = type(error.instance).__name__
        message = f"'{path}' must be of type {expected}, got {actual}"
    elif error.validator == "minLength" or (error.validator == "pattern" and "\\S" in str(error.validator_value)):
        message = f"'{path}' must be a non-empty string"
    elif error.validator == "pattern":
        if "https?://" in str(error.validator_value):
            message = f"'{path}' is not a valid URL. Use format: http:// or https://"
        else:
            message = f"'{path}' does not match required pattern"
    elif error.validator == "minItems":
        message = f"'{path}' must be a non-empty array"
    elif error.validator == "minimum":
        message = f"'{path}' must be >= {error.validator_value}, got {error.instance}"

    # Default message if no specific handler matched
    return message if message else f"{error.message} at {path}"
