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

"""Unit tests for the PDF report generator."""

import json
from pathlib import Path

from generator.report_generator import generate_pdf_report


def _generate(tmp_path, data, **overrides):
    pdf_path = overrides.get("pdf_path", tmp_path / "output.pdf")
    Path(pdf_path).write_text("fake pdf", encoding="utf-8")
    return generate_pdf_report(
        input_file=overrides.get("input_file", "/path/to/input.json"),
        output_file=str(pdf_path),
        template_pack_type=overrides.get("template_pack_type", "built-in"),
        template_pack_path=overrides.get("template_pack_path", "built-in"),
        data=data,
        pdf_path=str(pdf_path),
        errors=overrides.get("errors", []),
        warnings=overrides.get("warnings", []),
    )


def test_generate_pdf_report_creates_file(tmp_path):
    """generate_pdf_report writes a valid JSON report file."""
    report_path = _generate(tmp_path, {"items": []})

    assert Path(report_path).exists()
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    assert report["schema_version"] == "1.0"
    assert report["input_file"] == "/path/to/input.json"
    assert report["statistics"]["item_count"] == 0


def test_item_count_uses_items_key(tmp_path):
    """item_count counts the top-level items array."""
    data = {"items": [{"id": "US-1"}, {"id": "US-2"}, {"id": "US-3"}]}
    report_path = _generate(tmp_path, data)
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    assert report["statistics"]["item_count"] == 3


def test_item_count_falls_back_to_user_stories_key(tmp_path):
    """item_count falls back to user_stories when items is absent."""
    data = {"user_stories": [{"id": "US-1"}, {"id": "US-2"}]}
    report_path = _generate(tmp_path, data)
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    assert report["statistics"]["item_count"] == 2


def test_includes_file_size_and_template_pack(tmp_path):
    """Report records the PDF file size and the template pack metadata."""
    pdf_path = tmp_path / "output.pdf"
    pdf_path.write_bytes(b"some bytes here")
    report_path = _generate(
        tmp_path,
        {"items": []},
        pdf_path=pdf_path,
        template_pack_type="custom",
        template_pack_path="/custom/templates",
    )
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    assert report["statistics"]["file_size_bytes"] == pdf_path.stat().st_size
    assert report["template_pack"]["type"] == "custom"
    assert report["template_pack"]["path"] == "/custom/templates"


def test_preserves_input_warnings(tmp_path):
    """Report preserves caller-provided warnings."""
    warnings = [{"level": "warning", "message": "Custom warning"}]
    report_path = _generate(tmp_path, {"items": []}, warnings=warnings)
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    assert report["warnings"] == warnings


def test_report_schema_fields(tmp_path):
    """Report contains all expected top-level fields."""
    report_path = _generate(tmp_path, {"items": []})
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    for field in (
        "schema_version",
        "generated_at",
        "input_file",
        "output_file",
        "template_pack",
        "statistics",
        "errors",
        "warnings",
    ):
        assert field in report
