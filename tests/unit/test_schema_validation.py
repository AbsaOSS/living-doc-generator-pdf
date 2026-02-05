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

"""Unit tests for schema validation."""

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from generator.schema_validator import SchemaValidationError, validate_pdf_ready_json


# Sentinel for key deletion in mutation
_DELETE = object()


def _base_valid_data() -> dict[str, Any]:
    """Return a valid base document with a user story for mutation tests."""
    return {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test Doc",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 1, "included_items": 1, "excluded_items": 0},
        },
        "content": {
            "user_stories": [
                {
                    "id": "test-1",
                    "title": "Test Story",
                    "state": "open",
                    "tags": [],
                    "url": "https://example.com/issue/1",
                    "timestamps": {
                        "created": "2026-01-21T12:00:00Z",
                        "updated": "2026-01-21T12:00:00Z",
                    },
                    "sections": {},
                }
            ]
        },
    }


def _mutate(data: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """
    Apply a mutation to nested dict at dot-separated path.

    Use _DELETE sentinel to remove the key entirely.
    """
    result = copy.deepcopy(data)
    keys = path.split(".")
    target = result
    for key in keys[:-1]:
        if key.isdigit():
            target = target[int(key)]
        else:
            target = target[key]
    final_key: str | int = int(keys[-1]) if keys[-1].isdigit() else keys[-1]
    if value is _DELETE:
        del target[final_key]
    else:
        target[final_key] = value
    return result


# Parametrized invalid test cases: (test_id, path, value, error_pattern)
INVALID_CASES = [
    ("missing_schema_version", "schema_version", _DELETE, "Missing required field 'schema_version'"),
    ("wrong_schema_version", "schema_version", "2.0", "Invalid schema_version"),
    ("missing_meta", "meta", _DELETE, "Missing required field 'meta'"),
    ("missing_content", "content", _DELETE, "Missing required field 'content'"),
    ("empty_document_title", "meta.document_title", "", "must be a non-empty string"),
    ("empty_source_set", "meta.source_set", [], "must be a non-empty array"),
    ("negative_total_items", "meta.selection_summary.total_items", -1, "must be >= 0"),
    ("invalid_url", "content.user_stories.0.url", "not-a-url", "is not a valid URL"),
    ("wrong_type_title", "meta.document_title", 123, "must be of type string"),
    ("whitespace_only_version", "meta.document_version", "   ", "must be a non-empty string"),
]


@pytest.mark.parametrize(
    ("test_id", "path", "value", "error_pattern"),
    INVALID_CASES,
    ids=[case[0] for case in INVALID_CASES],
)
def test_invalid_data(
    tmp_path: Path, test_id: str, path: str, value: Any, error_pattern: str
) -> None:
    """Data-driven test for invalid JSON variations."""
    _ = test_id  # Used only for test ID
    data = _mutate(_base_valid_data(), path, value)
    test_file = tmp_path / "test.json"
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match=error_pattern):
        validate_pdf_ready_json(str(test_file))


def test_valid_minimal_json(tmp_path: Path) -> None:
    """Test that minimal valid JSON passes validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test Doc",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    result = validate_pdf_ready_json(str(test_file))
    assert result == data


def test_valid_full_json(tmp_path: Path) -> None:
    """Test that complete JSON with all fields passes validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Product Requirements - Release 2.1",
            "document_version": "2.1.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:AbsaOSS/living-doc-generator-pdf"],
            "selection_summary": {"total_items": 15, "included_items": 12, "excluded_items": 3},
            "run_context": {
                "ci_run_id": "123456",
                "triggered_by": "user@example.com",
                "branch": "main",
                "commit_sha": "abc123def456",
            },
        },
        "content": {
            "user_stories": [
                {
                    "id": "github:AbsaOSS/project#42",
                    "title": "User login with SSO",
                    "state": "open",
                    "tags": ["authentication", "priority:high"],
                    "url": "https://github.com/AbsaOSS/project/issues/42",
                    "timestamps": {"created": "2026-01-10T08:00:00Z", "updated": "2026-01-20T14:30:00Z"},
                    "sections": {
                        "description": "As a user, I want to log in using SSO...",
                        "business_value": "Reduces friction for enterprise users",
                        "preconditions": "SSO provider configured",
                        "acceptance_criteria": "- User can click SSO button\n- Redirect to provider\n- Return with session",
                        "user_guide": None,
                        "connections": "Related to #41, #43",
                        "last_edited": "Updated by alice@example.com on 2026-01-20",
                    },
                }
            ]
        },
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    result = validate_pdf_ready_json(str(test_file))
    assert result == data


def test_user_story_all_required_fields(tmp_path: Path) -> None:
    """Test that user story with all required fields passes validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 1, "included_items": 1, "excluded_items": 0},
        },
        "content": {
            "user_stories": [
                {
                    "id": "test-1",
                    "title": "Test Story",
                    "state": "open",
                    "tags": ["test"],
                    "url": "https://example.com/issue/1",
                    "timestamps": {"created": "2026-01-21T12:00:00Z", "updated": "2026-01-21T12:00:00Z"},
                    "sections": {"description": "Test description"},
                }
            ]
        },
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    result = validate_pdf_ready_json(str(test_file))
    assert len(result["content"]["user_stories"]) == 1


def test_file_not_found() -> None:
    """Test that missing file raises ValueError."""
    with pytest.raises(ValueError, match="File.*not found"):
        validate_pdf_ready_json("/nonexistent/file.json")


def test_invalid_json_file(tmp_path: Path) -> None:
    """Test that invalid JSON file raises ValueError."""
    test_file = tmp_path / "test.json"
    test_file.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(ValueError, match="contains invalid JSON"):
        validate_pdf_ready_json(str(test_file))


def test_schema_file_not_found(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test that missing schema file raises RuntimeError."""
    test_file = tmp_path / "test.json"
    test_file.write_text('{"schema_version": "1.0"}', encoding="utf-8")

    mocker.patch("builtins.open", side_effect=[open(test_file), FileNotFoundError("schema missing")])
    with pytest.raises(RuntimeError, match="Internal error: Schema file not found"):
        validate_pdf_ready_json(str(test_file))
