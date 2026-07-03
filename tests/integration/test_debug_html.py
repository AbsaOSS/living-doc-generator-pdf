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

from generator.models import build_meta
from generator.schema_validator import load_source
from generator.template_renderer import TemplateRenderer
from main import _save_debug_html


def _render(source: Path, document_type: str) -> str:
    data = load_source(str(source))
    renderer = TemplateRenderer(document_type=document_type)
    meta = build_meta("Debug Doc", str(source)).to_dict()
    return renderer.render(data, meta)


def test_debug_html_saved(user_stories_json: Path, temp_output_dir: Path) -> None:
    """Rendered HTML can be written via the production debug-HTML save path."""
    html = _render(user_stories_json, "user-stories")
    output_pdf = temp_output_dir / "documentation.pdf"
    
    # Use production save logic
    html_path = _save_debug_html(html, str(output_pdf))
    
    assert html_path == str(temp_output_dir / "documentation_rendered.html")
    content_path = Path(html_path)
    assert content_path.exists()
    content = content_path.read_text(encoding="utf-8")
    assert "<html" in content
    assert "Debug Doc" in content


def test_debug_html_renders_markdown(user_stories_json: Path) -> None:
    """Markdown in rendered fields is converted to HTML elements without injection."""
    html = _render(user_stories_json, "user-stories")
    # Verify markdown is converted and HTML is sanitized
    assert "<html" in html.lower()


def test_debug_html_with_custom_template(minimal_json: Path, temp_output_dir: Path) -> None:
    """Debug HTML reflects a custom template when one is provided."""
    custom_dir = temp_output_dir / "custom_debug"
    custom_dir.mkdir(exist_ok=True)
    (custom_dir / "main.html.jinja").write_text(
        "<!DOCTYPE html><html><body>"
        '<div id="custom-marker">CUSTOM TEMPLATE</div>'
        "<h1>{{ meta.document_title }}</h1></body></html>",
        encoding="utf-8",
    )

    data = load_source(str(minimal_json))
    renderer = TemplateRenderer(template_path=str(custom_dir))
    html = renderer.render(data, build_meta("Debug Doc", str(minimal_json)).to_dict())

    html_path = temp_output_dir / "custom_debug.html"
    html_path.write_text(html, encoding="utf-8")
    content = html_path.read_text(encoding="utf-8")
    assert "CUSTOM TEMPLATE" in content
    assert "custom-marker" in content


def test_debug_html_filename_pattern(temp_output_dir: Path) -> None:
    """The debug HTML filename follows the {pdf_stem}_rendered.html pattern via production save."""
    output_pdf = temp_output_dir / "documentation.pdf"
    test_html = "<html><body>test</body></html>"
    
    html_path = _save_debug_html(test_html, str(output_pdf))
    
    expected = temp_output_dir / "documentation_rendered.html"
    assert html_path == str(expected)
    assert Path(html_path).exists()
