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

"""Unit tests for PDF report generator."""

import json
from pathlib import Path

from generator.report_generator import generate_pdf_report


def test_generate_pdf_report_creates_file(tmp_path):
    """Test that generate_pdf_report creates a valid JSON file."""
    pdf_path = tmp_path / "output.pdf"
    pdf_path.write_text("fake pdf")

    pdf_ready_data = {
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

    report_path = generate_pdf_report(
        input_file="/path/to/input.json",
        output_file=str(pdf_path),
        template_pack_type="built-in",
        template_pack_path="built-in",
        pdf_ready_data=pdf_ready_data,
        pdf_path=str(pdf_path),
        errors=[],
        warnings=[],
    )

    assert Path(report_path).exists()
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    assert report["schema_version"] == "1.0"
    assert "generated_at" in report
    assert report["input_file"] == "/path/to/input.json"
    assert report["statistics"]["user_story_count"] == 0


def test_generate_pdf_report_includes_statistics(tmp_path):
    """Test that report includes correct statistics."""
    pdf_path = tmp_path / "output.pdf"
    pdf_path.write_bytes(b"fake pdf content with some bytes")

    pdf_ready_data = {
        "content": {
            "user_stories": [
                {"id": "story-1", "title": "Story 1", "sections": {"description": "Test"}},
                {"id": "story-2", "title": "Story 2", "sections": {"description": "Test"}},
                {"id": "story-3", "title": "Story 3", "sections": {"description": "Test"}},
            ]
        }
    }

    report_path = generate_pdf_report(
        input_file="/path/to/input.json",
        output_file=str(pdf_path),
        template_pack_type="custom",
        template_pack_path="/custom/templates",
        pdf_ready_data=pdf_ready_data,
        pdf_path=str(pdf_path),
        errors=[],
        warnings=[],
    )

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    assert report["statistics"]["user_story_count"] == 3
    assert report["statistics"]["file_size_bytes"] == pdf_path.stat().st_size
    assert report["template_pack"]["type"] == "custom"
    assert report["template_pack"]["path"] == "/custom/templates"


def test_generate_pdf_report_detects_missing_acceptance_criteria(tmp_path):
    """Test that report includes warnings for missing user story sections."""
    pdf_path = tmp_path / "output.pdf"
    pdf_path.write_text("fake pdf")

    pdf_ready_data = {
        "content": {
            "user_stories": [
                {
                    "id": "github:test/repo#1",
                    "title": "Story 1",
                    "sections": {"description": "Has description", "acceptance_criteria": "Has criteria"},
                },
                {
                    "id": "github:test/repo#2",
                    "title": "Story 2",
                    "sections": {"description": "Has description only"},
                },
                {
                    "id": "github:test/repo#3",
                    "title": "Story 3",
                    "sections": {},
                },
            ]
        }
    }

    report_path = generate_pdf_report(
        input_file="/path/to/input.json",
        output_file=str(pdf_path),
        template_pack_type="built-in",
        template_pack_path="built-in",
        pdf_ready_data=pdf_ready_data,
        pdf_path=str(pdf_path),
        errors=[],
        warnings=[],
    )

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    # Should have warnings for stories 2 and 3
    assert len(report["warnings"]) == 2
    assert any("github:test/repo#2" in w["message"] for w in report["warnings"])
    assert any("github:test/repo#3" in w["message"] for w in report["warnings"])
    assert all(w["level"] == "warning" for w in report["warnings"])


def test_generate_pdf_report_preserves_input_warnings(tmp_path):
    """Test that report preserves input warnings."""
    pdf_path = tmp_path / "output.pdf"
    pdf_path.write_text("fake pdf")

    pdf_ready_data = {"content": {"user_stories": []}}

    input_warnings = [{"level": "warning", "message": "Custom warning", "context": "test"}]

    report_path = generate_pdf_report(
        input_file="/path/to/input.json",
        output_file=str(pdf_path),
        template_pack_type="built-in",
        template_pack_path="built-in",
        pdf_ready_data=pdf_ready_data,
        pdf_path=str(pdf_path),
        errors=[],
        warnings=input_warnings,
    )

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    assert len(report["warnings"]) == 1
    assert report["warnings"][0]["message"] == "Custom warning"


def test_generate_pdf_report_schema_compliance(tmp_path):
    """Test that generated report follows the expected schema."""
    pdf_path = tmp_path / "output.pdf"
    pdf_path.write_text("fake pdf")

    pdf_ready_data = {"content": {"user_stories": []}}

    report_path = generate_pdf_report(
        input_file="/path/to/input.json",
        output_file=str(pdf_path),
        template_pack_type="built-in",
        template_pack_path="built-in",
        pdf_ready_data=pdf_ready_data,
        pdf_path=str(pdf_path),
        errors=[],
        warnings=[],
    )

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    # Check all required fields exist
    assert "schema_version" in report
    assert "generated_at" in report
    assert "input_file" in report
    assert "output_file" in report
    assert "template_pack" in report
    assert "statistics" in report
    assert "errors" in report
    assert "warnings" in report

    # Check template_pack structure
    assert "type" in report["template_pack"]
    assert "path" in report["template_pack"]

    # Check statistics structure
    assert "user_story_count" in report["statistics"]
    assert "total_pages" in report["statistics"]
    assert "file_size_bytes" in report["statistics"]
