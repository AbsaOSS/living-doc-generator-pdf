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

"""Integration tests for custom template override scenarios."""

from __future__ import annotations

from pathlib import Path

from generator.pdf_generator import PdfGenerator
from generator.schema_validator import validate_pdf_ready_json
from generator.template_renderer import TemplateRenderer


def test_custom_template_full_override(minimal_valid_json: Path, temp_output_dir: Path) -> None:
    """Test using a custom template that overrides all built-in templates."""
    # Create a custom template directory
    custom_template_dir = temp_output_dir / "custom_templates"
    custom_template_dir.mkdir(exist_ok=True)

    # Create a custom main template
    main_template = custom_template_dir / "main.html.jinja"
    main_template.write_text(
        """<!DOCTYPE html>
<html>
<head>
    <title>{{ meta.document_title }}</title>
    <style>
        body { font-family: Arial; }
        h1 { color: blue; }
    </style>
</head>
<body>
    <h1>CUSTOM TEMPLATE: {{ meta.document_title }}</h1>
    <p>Version: {{ meta.document_version }}</p>
    <p>Generated: {{ meta.generated_at }}</p>
</body>
</html>"""
    )

    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(minimal_valid_json))

    # Render HTML with custom template
    renderer = TemplateRenderer(str(custom_template_dir))
    html = renderer.render(pdf_ready_data)

    # Verify custom template was used
    assert "CUSTOM TEMPLATE:" in html
    assert "color: blue;" in html

    # Generate PDF
    output_pdf = temp_output_dir / "custom_template.pdf"
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), str(custom_template_dir))

    # Verify PDF was created
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0


def test_custom_template_partial_override(minimal_valid_json: Path, temp_output_dir: Path) -> None:
    """Test custom template with partial override (fallback to built-in)."""
    # Create a custom template directory with only a cover template
    custom_template_dir = temp_output_dir / "partial_custom"
    custom_template_dir.mkdir(exist_ok=True)

    # Create only a custom cover template
    cover_template = custom_template_dir / "cover.html.jinja"
    cover_template.write_text(
        """<div class="custom-cover">
    <h1>{{ meta.document_title }} - CUSTOM COVER</h1>
</div>"""
    )

    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(minimal_valid_json))

    # Render HTML - should use custom cover but built-in main
    renderer = TemplateRenderer(str(custom_template_dir))
    html = renderer.render(pdf_ready_data)

    # Verify custom cover template was used
    assert "CUSTOM COVER" in html


def test_template_with_styles(minimal_valid_json: Path, temp_output_dir: Path) -> None:
    """Test custom template with custom styles.css."""
    # Create a custom template directory
    custom_template_dir = temp_output_dir / "custom_styles"
    custom_template_dir.mkdir(exist_ok=True)

    # Create a custom styles.css
    styles_file = custom_template_dir / "styles.css"
    styles_file.write_text(
        """body {
    background-color: #f0f0f0;
    font-family: 'Courier New', monospace;
}
h1 {
    color: red;
    font-size: 48px;
}"""
    )

    # Create a simple main template that uses the styles
    main_template = custom_template_dir / "main.html.jinja"
    main_template.write_text(
        """<!DOCTYPE html>
<html>
<head>
    <title>{{ meta.document_title }}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>{{ meta.document_title }}</h1>
</body>
</html>"""
    )

    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(minimal_valid_json))

    # Render HTML
    renderer = TemplateRenderer(str(custom_template_dir))
    html = renderer.render(pdf_ready_data)

    # Generate PDF
    output_pdf = temp_output_dir / "custom_styles.pdf"
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), str(custom_template_dir))

    # Verify PDF was created
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0
