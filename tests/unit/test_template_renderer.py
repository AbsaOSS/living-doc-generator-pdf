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

"""Unit tests for template renderer."""

from pathlib import Path

import pytest

from generator.template_renderer import TemplateError, TemplateRenderer


@pytest.fixture
def minimal_pdf_data() -> dict:
    """Return minimal valid pdf_ready data."""
    return {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test Document",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["github:test/repo"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }


@pytest.fixture
def full_pdf_data() -> dict:
    """Return full pdf_ready data with user stories."""
    return {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test Document",
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
                    "tags": ["test", "priority:high"],
                    "url": "https://example.com/issue/1",
                    "timestamps": {
                        "created": "2026-01-21T12:00:00Z",
                        "updated": "2026-01-21T12:00:00Z",
                    },
                    "sections": {
                        "description": "## Description\n\nThis is a test story.",
                        "business_value": "High value for testing",
                        "preconditions": None,
                        "acceptance_criteria": "- [ ] Test passes\n- [x] Code works",
                        "user_guide": None,
                        "connections": None,
                        "last_edited": None,
                    },
                }
            ]
        },
    }


def test_render_with_built_in_templates(minimal_pdf_data: dict) -> None:
    """Test rendering with built-in templates works."""
    renderer = TemplateRenderer()
    html = renderer.render(minimal_pdf_data)

    # Check basic structure
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "Test Document" in html
    assert "1.0.0" in html


def test_render_with_custom_templates(tmp_path: Path, minimal_pdf_data: dict) -> None:
    """Test custom template override works."""
    # Create custom template directory
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()

    # Create custom main template
    custom_main = custom_dir / "main.html.jinja"
    custom_main.write_text(
        "<!DOCTYPE html>\n<html><body><h1>CUSTOM: {{ meta.document_title }}</h1></body></html>"
    )

    renderer = TemplateRenderer(str(custom_dir))
    html = renderer.render(minimal_pdf_data)

    assert "CUSTOM: Test Document" in html


def test_missing_template_error(tmp_path: Path) -> None:
    """Test error handling for missing templates."""
    # Create custom directory with a template that references a missing include
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()

    # Create template that tries to include a non-existent template
    custom_main = custom_dir / "main.html.jinja"
    custom_main.write_text("<!DOCTYPE html>\n{% include 'nonexistent.html.jinja' %}")

    renderer = TemplateRenderer(str(custom_dir))

    data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["test"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }

    with pytest.raises(TemplateError, match="Template .* not found"):
        renderer.render(data)


def test_template_syntax_error(tmp_path: Path, minimal_pdf_data: dict) -> None:
    """Test error handling for template syntax errors."""
    # Create custom template with syntax error
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()

    # Create template with invalid Jinja2 syntax
    custom_main = custom_dir / "main.html.jinja"
    custom_main.write_text("<!DOCTYPE html>\n<html><body>{{ unclosed_tag </body></html>")

    renderer = TemplateRenderer(str(custom_dir))

    with pytest.raises(TemplateError, match="Syntax error"):
        renderer.render(minimal_pdf_data)


def test_template_receives_all_variables(full_pdf_data: dict) -> None:
    """Test that all schema variables are available in templates."""
    renderer = TemplateRenderer()
    html = renderer.render(full_pdf_data)

    # Check metadata
    assert "Test Document" in html
    assert "1.0.0" in html

    # Check user story
    assert "test-1" in html
    assert "Test Story" in html
    assert "open" in html
    assert "test" in html
    assert "priority:high" in html
    assert "https://example.com/issue/1" in html

    # Check sections
    assert "Description" in html
    assert "This is a test story" in html
    assert "Business Value" in html
    assert "High value for testing" in html
    assert "Acceptance Criteria" in html


def test_render_handles_none_sections(full_pdf_data: dict) -> None:
    """Test that None sections are handled gracefully."""
    # Ensure some sections are None
    full_pdf_data["content"]["user_stories"][0]["sections"]["preconditions"] = None
    full_pdf_data["content"]["user_stories"][0]["sections"]["user_guide"] = None

    renderer = TemplateRenderer()
    html = renderer.render(full_pdf_data)

    # Should render without errors
    assert "Test Story" in html


def test_markdown_filter_in_template(full_pdf_data: dict) -> None:
    """Test that markdown filter works in templates."""
    renderer = TemplateRenderer()
    html = renderer.render(full_pdf_data)

    # Markdown heading should be converted to HTML
    assert "<h2>Description</h2>" in html


def test_format_datetime_filter_in_template(full_pdf_data: dict) -> None:
    """Test that format_datetime filter works in templates."""
    renderer = TemplateRenderer()
    html = renderer.render(full_pdf_data)

    # ISO timestamp should be formatted
    assert "2026-01-21" in html


def test_custom_template_fallback_to_builtin(tmp_path: Path, minimal_pdf_data: dict) -> None:
    """Test that missing custom templates fall back to built-in."""
    # Create custom directory with only one template
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()

    # Create custom cover template only
    custom_cover = custom_dir / "cover.html.jinja"
    custom_cover.write_text("<div class='custom-cover'>CUSTOM COVER: {{ meta.document_title }}</div>")

    # Renderer should use custom cover but built-in main and other templates
    renderer = TemplateRenderer(str(custom_dir))
    html = renderer.render(minimal_pdf_data)

    assert "CUSTOM COVER" in html
    assert "<!DOCTYPE html>" in html  # From built-in main.html.jinja
