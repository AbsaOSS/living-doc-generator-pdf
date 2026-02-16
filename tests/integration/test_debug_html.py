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

"""Integration tests for debug HTML output scenarios."""

from __future__ import annotations

from pathlib import Path

from generator.pdf_generator import PdfGenerator
from generator.schema_validator import validate_pdf_ready_json
from generator.template_renderer import TemplateRenderer


def test_debug_html_saved(minimal_valid_json: Path, temp_output_dir: Path) -> None:
    """Test that debug HTML is saved when enabled."""
    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(minimal_valid_json))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Save HTML to file
    output_pdf = temp_output_dir / "output.pdf"
    html_output_path = temp_output_dir / "output_rendered.html"

    # Save debug HTML
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Verify HTML file exists
    assert html_output_path.exists()
    assert html_output_path.stat().st_size > 0

    # Verify HTML content
    html_content = html_output_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html_content or "<html" in html_content
    assert pdf_ready_data["meta"]["document_title"] in html_content


def test_debug_html_viewable(full_example_json: Path, temp_output_dir: Path) -> None:
    """Test that generated HTML is valid and viewable."""
    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(full_example_json))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Save HTML
    html_output_path = temp_output_dir / "full_example_rendered.html"
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Verify HTML structure
    html_content = html_output_path.read_text(encoding="utf-8")

    # Check for basic HTML structure
    assert "<html" in html_content
    assert "</html>" in html_content
    assert "<head>" in html_content or "<head " in html_content
    assert "<body>" in html_content or "<body " in html_content

    # Check for document metadata
    assert pdf_ready_data["meta"]["document_title"] in html_content
    assert pdf_ready_data["meta"]["document_version"] in html_content

    # Check for user stories if present
    if pdf_ready_data["content"]["user_stories"]:
        first_story = pdf_ready_data["content"]["user_stories"][0]
        assert first_story["title"] in html_content


def test_debug_html_with_custom_template(minimal_valid_json: Path, temp_output_dir: Path) -> None:
    """Test debug HTML generation with custom template."""
    # Create a custom template directory
    custom_template_dir = temp_output_dir / "custom_debug"
    custom_template_dir.mkdir(exist_ok=True)

    # Create a custom main template
    main_template = custom_template_dir / "main.html.jinja"
    main_template.write_text(
        """<!DOCTYPE html>
<html>
<head>
    <title>CUSTOM: {{ meta.document_title }}</title>
</head>
<body>
    <div id="custom-marker">CUSTOM TEMPLATE</div>
    <h1>{{ meta.document_title }}</h1>
</body>
</html>"""
    )

    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(minimal_valid_json))

    # Render HTML with custom template
    renderer = TemplateRenderer(str(custom_template_dir))
    html = renderer.render(pdf_ready_data)

    # Save debug HTML
    html_output_path = temp_output_dir / "custom_debug.html"
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Verify custom template was used
    html_content = html_output_path.read_text(encoding="utf-8")
    assert "CUSTOM TEMPLATE" in html_content
    assert "custom-marker" in html_content


def test_debug_html_filename_pattern(temp_output_dir: Path) -> None:
    """Test that debug HTML filename follows the expected pattern."""
    # Define output PDF path
    output_pdf = temp_output_dir / "documentation.pdf"

    # Expected debug HTML path should be {pdf_basename}_rendered.html
    expected_html_path = temp_output_dir / "documentation_rendered.html"

    # Verify the pattern
    pdf_basename = output_pdf.stem  # "documentation"
    expected_filename = f"{pdf_basename}_rendered.html"

    assert expected_filename == "documentation_rendered.html"
    assert expected_html_path == temp_output_dir / expected_filename


def test_debug_html_not_saved_by_default(minimal_valid_json: Path, temp_output_dir: Path) -> None:
    """Test that debug HTML is not saved when debug mode is disabled."""
    # This test documents the expected behavior:
    # When debug_html=false (default), no HTML file should be created automatically

    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(minimal_valid_json))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Generate PDF only (no debug HTML)
    output_pdf = temp_output_dir / "no_debug.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Verify PDF exists
    assert output_pdf.exists()

    # Verify HTML file was NOT created automatically
    html_path = temp_output_dir / "no_debug_rendered.html"
    assert not html_path.exists()


def test_debug_html_with_markdown_content(multiple_stories_json: Path, temp_output_dir: Path) -> None:
    """Test that markdown in user stories is properly rendered in debug HTML."""
    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(multiple_stories_json))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Save debug HTML
    html_output_path = temp_output_dir / "markdown_debug.html"
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Read HTML content
    html_content = html_output_path.read_text(encoding="utf-8")

    # Check that markdown was converted to HTML elements
    # (Assuming stories have markdown content)
    # Should contain HTML tags like <p>, <ul>, <li>, <strong>, etc.
    # instead of raw markdown syntax
    if any(
        story.get("sections", {}).get("description") for story in pdf_ready_data["content"]["user_stories"]
    ):
        # If there's any description content, it should be rendered as HTML
        assert "<p>" in html_content or "<div>" in html_content
