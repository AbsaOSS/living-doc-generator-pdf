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

import json
from pathlib import Path

import pytest

from generator.schema_validator import SchemaValidationError, validate_pdf_ready_json


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


def test_invalid_missing_schema_version(tmp_path: Path) -> None:
    """Test that missing schema_version field fails validation."""
    test_file = tmp_path / "test.json"
    data = {
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="Missing required field 'schema_version'"):
        validate_pdf_ready_json(str(test_file))


def test_invalid_wrong_schema_version(tmp_path: Path) -> None:
    """Test that non-'1.0' schema version fails validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "2.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="Invalid schema_version"):
        validate_pdf_ready_json(str(test_file))


def test_invalid_missing_meta(tmp_path: Path) -> None:
    """Test that missing meta section fails validation."""
    test_file = tmp_path / "test.json"
    data = {"schema_version": "1.0", "content": {"user_stories": []}}
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="Missing required field 'meta'"):
        validate_pdf_ready_json(str(test_file))


def test_invalid_missing_content(tmp_path: Path) -> None:
    """Test that missing content section fails validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="Missing required field 'content'"):
        validate_pdf_ready_json(str(test_file))


def test_invalid_empty_document_title(tmp_path: Path) -> None:
    """Test that empty document_title fails validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="must be a non-empty string"):
        validate_pdf_ready_json(str(test_file))


def test_invalid_timestamp_format(tmp_path: Path) -> None:
    """Test that invalid ISO 8601 timestamp fails validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "invalid-timestamp",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="is not a valid ISO 8601 timestamp"):
        validate_pdf_ready_json(str(test_file))


def test_invalid_url_format(tmp_path: Path) -> None:
    """Test that invalid URL format fails validation."""
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
                    "tags": [],
                    "url": "not-a-url",
                    "timestamps": {"created": "2026-01-21T12:00:00Z", "updated": "2026-01-21T12:00:00Z"},
                    "sections": {},
                }
            ]
        },
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="is not a valid URL"):
        validate_pdf_ready_json(str(test_file))


def test_invalid_empty_source_set(tmp_path: Path) -> None:
    """Test that empty source_set array fails validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": [],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="must be a non-empty array"):
        validate_pdf_ready_json(str(test_file))


def test_invalid_negative_total_items(tmp_path: Path) -> None:
    """Test that negative integer for total_items fails validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": -1, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="must be >= 0"):
        validate_pdf_ready_json(str(test_file))


def test_valid_empty_user_stories(tmp_path: Path) -> None:
    """Test that empty user_stories array passes validation."""
    test_file = tmp_path / "test.json"
    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    test_file.write_text(json.dumps(data), encoding="utf-8")

    result = validate_pdf_ready_json(str(test_file))
    assert result["content"]["user_stories"] == []


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
