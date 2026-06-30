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

"""Integration tests for edge cases: empty data, large content, special characters."""

from __future__ import annotations

import json
from pathlib import Path

from generator.models import build_meta
from generator.pdf_generator import PdfGenerator
from generator.schema_validator import load_source
from generator.template_renderer import TemplateRenderer


def _write(tmp: Path, name: str, payload: dict) -> Path:
    path = tmp / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _render_pdf(source: Path, document_type: str, output_pdf: Path) -> str:
    data = load_source(str(source))
    renderer = TemplateRenderer(document_type=document_type)
    html = renderer.render(data, build_meta("Edge", str(source)).to_dict())
    PdfGenerator().generate_pdf(html, str(output_pdf), renderer.base_dir)
    return html


def test_empty_items_array(temp_output_dir: Path) -> None:
    """An empty items array still renders a PDF."""
    source = _write(temp_output_dir, "empty.json", {"items": []})
    output_pdf = temp_output_dir / "empty.pdf"
    _render_pdf(source, "user-stories", output_pdf)
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0


def test_item_with_minimal_fields(temp_output_dir: Path) -> None:
    """An item with only id and title renders without optional fields."""
    payload = {"items": [{"id": "US-1", "title": "Minimal", "acceptance_criteria": []}]}
    source = _write(temp_output_dir, "minimal_item.json", payload)
    output_pdf = temp_output_dir / "minimal_item.pdf"
    html = _render_pdf(source, "user-stories", output_pdf)
    assert "Minimal" in html
    assert output_pdf.exists()


def test_large_markdown_content(temp_output_dir: Path) -> None:
    """Large markdown content renders into a reasonably sized PDF."""
    large_markdown = "# Large Content\n\n" + "\n\n".join(
        f"## Section {i}\n\nParagraph {i} with content." for i in range(100)
    )
    payload = {
        "items": [
            {
                "id": "US-1",
                "title": "Large Content Story",
                "description": large_markdown,
                "acceptance_criteria": [{"id": "AC-1", "description": large_markdown}],
            }
        ]
    }
    source = _write(temp_output_dir, "large.json", payload)
    output_pdf = temp_output_dir / "large.pdf"
    html = _render_pdf(source, "user-stories", output_pdf)

    assert "Section 50" in html
    assert "Section 99" in html
    assert output_pdf.stat().st_size > 10000


def test_special_characters_in_content(temp_output_dir: Path) -> None:
    """Unicode and special characters render and are HTML-escaped."""
    payload = {
        "items": [
            {
                "id": "US-1",
                "title": 'Story with émojis and <special> & "chars"',
                "description": "Description with special chars: <tag> & 'quotes' € £ ¥ 中文",
                "acceptance_criteria": [
                    {"id": "AC-1", "description": "Test émoji content"},
                    {"id": "AC-2", "description": "Test Chinese: 中文"},
                ],
            }
        ]
    }
    source = _write(temp_output_dir, "special.json", payload)
    output_pdf = temp_output_dir / "special.pdf"
    html = _render_pdf(source, "user-stories", output_pdf)

    assert "中文" in html
    # Autoescaping renders angle brackets safely.
    assert "<special>" not in html
    assert output_pdf.exists()
