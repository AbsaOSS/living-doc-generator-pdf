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

"""Integration tests for end-to-end PDF generation scenarios."""

from __future__ import annotations

import json
from pathlib import Path

from generator.pdf_generator import PdfGenerator
from generator.report_generator import generate_pdf_report
from generator.schema_validator import validate_pdf_ready_json
from generator.template_renderer import TemplateRenderer


def test_generate_pdf_minimal(minimal_valid_json: Path, temp_output_dir: Path) -> None:
    """Test generating PDF from minimal valid JSON."""
    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(minimal_valid_json))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Generate PDF
    output_pdf = temp_output_dir / "minimal.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Verify PDF exists and has valid structure
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0

    # Verify PDF starts with PDF magic bytes
    with open(output_pdf, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-"


def test_generate_pdf_with_stories(multiple_stories_json: Path, temp_output_dir: Path) -> None:
    """Test generating PDF with multiple user stories."""
    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(multiple_stories_json))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Generate PDF
    output_pdf = temp_output_dir / "multiple_stories.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Verify PDF exists and has valid structure
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0

    # Verify PDF is larger than minimal (has more content)
    minimal_pdf = temp_output_dir / "minimal.pdf"
    if minimal_pdf.exists():
        assert output_pdf.stat().st_size > minimal_pdf.stat().st_size


def test_generate_pdf_full_example(full_example_json: Path, temp_output_dir: Path) -> None:
    """Test generating PDF from full example with all fields."""
    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(full_example_json))

    # Render HTML
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)

    # Generate PDF
    output_pdf = temp_output_dir / "full_example.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Verify PDF exists
    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0

    # Verify PDF magic bytes
    with open(output_pdf, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-"


def test_pdf_report_created(minimal_valid_json: Path, temp_output_dir: Path) -> None:
    """Test that pdf_report.json is created with correct structure."""
    # Validate and load the JSON
    pdf_ready_data = validate_pdf_ready_json(str(minimal_valid_json))

    # Render HTML and generate PDF
    renderer = TemplateRenderer(None)
    html = renderer.render(pdf_ready_data)
    output_pdf = temp_output_dir / "test_report.pdf"
    template_dir = str(Path(__file__).parent.parent.parent / "generator" / "templates")
    generator = PdfGenerator()
    generator.generate_pdf(html, str(output_pdf), template_dir)

    # Generate report (it creates pdf_report.json in same dir as PDF)
    report_path_str = generate_pdf_report(
        input_file=str(minimal_valid_json),
        output_file=str(output_pdf),
        template_pack_type="built-in",
        template_pack_path="built-in",
        pdf_ready_data=pdf_ready_data,
        pdf_path=str(output_pdf),
        errors=[],
        warnings=[],
    )

    # Verify report exists
    report_path = Path(report_path_str)
    assert report_path.exists()

    # Load and verify report structure
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    assert report["schema_version"] == "1.0"
    assert "generated_at" in report
    assert report["input_file"] == str(minimal_valid_json)
    assert report["output_file"] == str(output_pdf)
    assert report["template_pack"]["type"] == "built-in"
    assert "statistics" in report
    assert "user_story_count" in report["statistics"]
    assert "file_size_bytes" in report["statistics"]
    assert "errors" in report
    assert "warnings" in report
