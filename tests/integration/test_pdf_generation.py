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

"""Integration tests for end-to-end PDF generation across document types."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from generator.models import build_meta
from generator.pdf_generator import PdfGenerator
from generator.report_generator import generate_pdf_report
from generator.schema_validator import load_source
from generator.template_renderer import TemplateRenderer


def _render_to_pdf(source: Path, document_type: str, output_pdf: Path) -> str:
    data = load_source(str(source))
    renderer = TemplateRenderer(document_type=document_type)
    meta = build_meta("Integration Test", str(source)).to_dict()
    html = renderer.render(data, meta)
    PdfGenerator().generate_pdf(html, str(output_pdf), renderer.base_dir)
    return html


@pytest.mark.parametrize(
    "fixture_name, document_type",
    [
        ("user_stories_json", "user-stories"),
        ("ui_tests_json", "ui-test-catalog"),
        ("coverage_matrix_json", "coverage-matrix"),
    ],
)
def test_generate_pdf_per_document_type(
    request, fixture_name: str, document_type: str, temp_output_dir: Path
) -> None:
    """Each built-in document type renders a valid PDF end-to-end."""
    source = request.getfixturevalue(fixture_name)
    output_pdf = temp_output_dir / f"{document_type}.pdf"

    _render_to_pdf(source, document_type, output_pdf)

    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0
    with open(output_pdf, "rb") as f:
        assert f.read(5) == b"%PDF-"


def test_generate_pdf_minimal(minimal_json: Path, temp_output_dir: Path) -> None:
    """An empty items list still renders a valid PDF."""
    output_pdf = temp_output_dir / "minimal.pdf"
    _render_to_pdf(minimal_json, "user-stories", output_pdf)

    assert output_pdf.exists()
    with open(output_pdf, "rb") as f:
        assert f.read(5) == b"%PDF-"


def test_pdf_report_created(user_stories_json: Path, temp_output_dir: Path) -> None:
    """pdf_report.json is created with the expected structure and item count."""
    output_pdf = temp_output_dir / "report.pdf"
    _render_to_pdf(user_stories_json, "user-stories", output_pdf)

    data = load_source(str(user_stories_json))
    report_path = generate_pdf_report(
        input_file=str(user_stories_json),
        output_file=str(output_pdf),
        template_pack_type="built-in",
        template_pack_path="user-stories",
        data=data,
        pdf_path=str(output_pdf),
        errors=[],
        warnings=[],
    )

    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    assert report["schema_version"] == "1.0"
    assert report["input_file"] == str(user_stories_json)
    assert report["template_pack"]["type"] == "built-in"
    assert report["statistics"]["item_count"] == 3
    assert "file_size_bytes" in report["statistics"]
