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

"""Integration tests for edge cases: large files, empty arrays, boundary conditions."""

from __future__ import annotations

import json
from pathlib import Path

from generator.pdf_generator import PdfGenerator
from generator.schema_validator import validate_pdf_ready_json
from generator.template_renderer import TemplateRenderer


def test_empty_user_stories_array(temp_output_dir: Path) -> None:
    """Test generating PDF with empty user_stories array."""
    # Create JSON with empty user_stories
    empty_stories_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Empty Document",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }

    # Write to file
    json_file = temp_output_dir / "empty_stories.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(empty_stories_data, f, indent=2)

    # Validate and load
    pdf_ready_data = validate_pdf_ready_json(str(json_file))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Generate PDF
    output_pdf = temp_output_dir / "empty_stories.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Verify PDF was created
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0


def test_user_story_with_minimal_sections(temp_output_dir: Path) -> None:
    """Test user story with only required fields (no optional sections)."""
    minimal_story_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Minimal Story",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 1, "included_items": 1, "excluded_items": 0},
        },
        "content": {
            "user_stories": [
                {
                    "id": "github:test/repo#1",
                    "title": "Minimal User Story",
                    "state": "open",
                    "tags": [],
                    "url": "https://github.com/test/repo/issues/1",
                    "timestamps": {
                        "created": "2026-01-20T10:00:00Z",
                        "updated": "2026-01-20T10:00:00Z",
                    },
                    "sections": {},  # No sections at all
                }
            ]
        },
    }

    # Write to file
    json_file = temp_output_dir / "minimal_story.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(minimal_story_data, f, indent=2)

    # Validate and load
    pdf_ready_data = validate_pdf_ready_json(str(json_file))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Generate PDF
    output_pdf = temp_output_dir / "minimal_story.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Verify PDF was created
    assert output_pdf.exists()


def test_large_markdown_content(temp_output_dir: Path) -> None:
    """Test user story with very large markdown content in sections."""
    # Create a large markdown string (simulating a long description)
    large_markdown = "# Large Content\n\n" + "\n\n".join(
        [f"## Section {i}\n\nThis is paragraph {i} with content." for i in range(100)]
    )

    large_content_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Large Content Document",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 1, "included_items": 1, "excluded_items": 0},
        },
        "content": {
            "user_stories": [
                {
                    "id": "github:test/repo#1",
                    "title": "Story with Large Content",
                    "state": "open",
                    "tags": ["documentation"],
                    "url": "https://github.com/test/repo/issues/1",
                    "timestamps": {
                        "created": "2026-01-20T10:00:00Z",
                        "updated": "2026-01-20T10:00:00Z",
                    },
                    "sections": {"description": large_markdown, "acceptance_criteria": large_markdown},
                }
            ]
        },
    }

    # Write to file
    json_file = temp_output_dir / "large_content.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(large_content_data, f, indent=2)

    # Validate and load
    pdf_ready_data = validate_pdf_ready_json(str(json_file))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Verify HTML contains the content
    assert "Section 50" in html
    assert "Section 99" in html

    # Generate PDF
    output_pdf = temp_output_dir / "large_content.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Verify PDF was created and is larger due to content
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 10000  # Should be reasonably large


def test_special_characters_in_content(temp_output_dir: Path) -> None:
    """Test handling of special characters and Unicode in content."""
    special_chars_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Special Characters: <>&\"' éàü 中文 🎉",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 1, "included_items": 1, "excluded_items": 0},
        },
        "content": {
            "user_stories": [
                {
                    "id": "github:test/repo#1",
                    "title": "Story with émojis 🎉 and <special> & \"chars\"",
                    "state": "open",
                    "tags": ["bug", "enhancement-中文"],
                    "url": "https://github.com/test/repo/issues/1",
                    "timestamps": {
                        "created": "2026-01-20T10:00:00Z",
                        "updated": "2026-01-20T10:00:00Z",
                    },
                    "sections": {
                        "description": "Description with **special** chars: <tag> & 'quotes' \"double\" € £ ¥",
                        "acceptance_criteria": "- [ ] Test émoji: 🎉\n- [x] Test Chinese: 中文\n- [ ] Test math: ∑∫∂",
                    },
                }
            ]
        },
    }

    # Write to file
    json_file = temp_output_dir / "special_chars.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(special_chars_data, f, ensure_ascii=False, indent=2)

    # Validate and load
    pdf_ready_data = validate_pdf_ready_json(str(json_file))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Verify special characters are in HTML (properly escaped)
    assert "éàü" in html
    assert "中文" in html

    # Generate PDF
    output_pdf = temp_output_dir / "special_chars.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Verify PDF was created
    assert output_pdf.exists()


def test_long_urls_and_ids(temp_output_dir: Path) -> None:
    """Test handling of very long URLs and IDs."""
    long_url = "https://github.com/organization/very-long-repository-name-that-goes-on-and-on/" + "issues/123456"
    long_id = "github:organization/very-long-repository-name-that-goes-on-and-on#123456"

    long_urls_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Long URLs Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": [
                "github:organization/very-long-repository-name-that-goes-on-and-on",
                "jira:project-with-long-name",
            ],
            "selection_summary": {"total_items": 1, "included_items": 1, "excluded_items": 0},
        },
        "content": {
            "user_stories": [
                {
                    "id": long_id,
                    "title": "Story with Long URL",
                    "state": "open",
                    "tags": ["label-with-very-long-name-that-should-wrap-properly"],
                    "url": long_url,
                    "timestamps": {
                        "created": "2026-01-20T10:00:00Z",
                        "updated": "2026-01-20T10:00:00Z",
                    },
                    "sections": {"description": "Test story"},
                }
            ]
        },
    }

    # Write to file
    json_file = temp_output_dir / "long_urls.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(long_urls_data, f, indent=2)

    # Validate and load
    pdf_ready_data = validate_pdf_ready_json(str(json_file))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Generate PDF
    output_pdf = temp_output_dir / "long_urls.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Verify PDF was created
    assert output_pdf.exists()
