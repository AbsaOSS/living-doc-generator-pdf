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

from generator.models import build_meta
from generator.pdf_generator import PdfGenerator
from generator.schema_validator import load_source
from generator.template_renderer import TemplateRenderer


def _meta(source: Path) -> dict:
    return build_meta("Custom", str(source)).to_dict()


def test_custom_template_full_override(minimal_json: Path, temp_output_dir: Path) -> None:
    """A self-contained custom template directory replaces the built-in set."""
    custom_dir = temp_output_dir / "custom_templates"
    custom_dir.mkdir(exist_ok=True)
    (custom_dir / "main.html.jinja").write_text(
        "<!DOCTYPE html><html><head><title>{{ meta.document_title }}</title>"
        "<style>h1 { color: blue; }</style></head>"
        "<body><h1>CUSTOM TEMPLATE: {{ meta.document_title }}</h1>"
        "<p>Items: {{ data.get('items', []) | length }}</p></body></html>",
        encoding="utf-8",
    )

    data = load_source(str(minimal_json))
    renderer = TemplateRenderer(template_path=str(custom_dir))
    html = renderer.render(data, _meta(minimal_json))

    assert "CUSTOM TEMPLATE:" in html
    assert "color: blue;" in html

    output_pdf = temp_output_dir / "custom_template.pdf"
    PdfGenerator().generate_pdf(html, str(output_pdf), renderer.base_dir)
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0


def test_partial_override_falls_back_to_builtin(user_stories_json: Path, temp_output_dir: Path) -> None:
    """A partial override directory falls back to the built-in set for missing partials."""
    custom_dir = temp_output_dir / "partial_custom"
    custom_dir.mkdir(exist_ok=True)
    # Override only the cover partial; main + others come from the built-in set.
    (custom_dir / "cover.html.jinja").write_text(
        '<div class="custom-cover"><h1>{{ meta.document_title }} - CUSTOM COVER</h1></div>',
        encoding="utf-8",
    )

    data = load_source(str(user_stories_json))
    renderer = TemplateRenderer(template_path=str(custom_dir), document_type="user-stories")
    html = renderer.render(data, _meta(user_stories_json))

    assert "CUSTOM COVER" in html
    # Built-in main still rendered the user stories.
    assert "US-1" in html


def test_custom_template_with_styles(minimal_json: Path, temp_output_dir: Path) -> None:
    """A custom template can reference its own styles.css via base_url."""
    custom_dir = temp_output_dir / "custom_styles"
    custom_dir.mkdir(exist_ok=True)
    (custom_dir / "styles.css").write_text("h1 { color: red; }", encoding="utf-8")
    (custom_dir / "main.html.jinja").write_text(
        "<!DOCTYPE html><html><head>"
        '<link rel="stylesheet" href="styles.css">'
        "</head><body><h1>{{ meta.document_title }}</h1></body></html>",
        encoding="utf-8",
    )

    data = load_source(str(minimal_json))
    renderer = TemplateRenderer(template_path=str(custom_dir))
    html = renderer.render(data, _meta(minimal_json))

    output_pdf = temp_output_dir / "custom_styles.pdf"
    PdfGenerator().generate_pdf(html, str(output_pdf), renderer.base_dir)
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0
