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

"""Golden test: ``generator-pdf`` renders ``toolkit``'s canonical ``generator-ready`` output.

``generator-pdf`` now consumes the normalized ``{meta, content}`` envelope
directly: the ``technical-project`` document type validates a source against the
vendored ``generator-ready-v1.0.0-schema.json`` and renders ``content.user_stories``.
These tests prove the actual ``examples/generator-ready.json`` file flows through
that path unchanged.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from generator.models import build_meta
from generator.pdf_generator import PdfGenerator
from generator.report_generator import generate_pdf_report
from generator.schema_validator import load_source
from generator.template_renderer import TemplateRenderer
from generator.utils.constants import DEFAULT_GENERATOR_READY_SCHEMA_PATH


def _render(data: dict, source: Path, output_pdf: Path, meta: dict | None = None) -> str:
    renderer = TemplateRenderer(document_type="technical-project")
    if meta is None:
        meta = build_meta("Generator-Ready Golden", str(source)).to_dict()
    html = renderer.render(data, meta)
    PdfGenerator().generate_pdf(html, str(output_pdf), renderer.base_dir)
    return html


def _item_count(source: Path, data: dict, output_pdf: Path) -> int:
    report_path = generate_pdf_report(
        input_file=str(source),
        output_file=str(output_pdf),
        template_pack_type="built-in",
        template_pack_path="technical-project",
        data=data,
        pdf_path=str(output_pdf),
        errors=[],
        warnings=[],
    )
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    return report["statistics"]["item_count"]


def test_generator_ready_validates_against_vendored_schema(generator_ready_json: Path) -> None:
    """The shipped example validates against the vendored canonical schema with no schema-path override."""
    data = load_source(str(generator_ready_json), DEFAULT_GENERATOR_READY_SCHEMA_PATH)

    assert data["schema_version"] == "generator-ready-v1.0.0"
    assert [s["id"] for s in data["content"]["user_stories"]] == [
        "AbsaOSS/living-doc-example/US-1",
        "AbsaOSS/living-doc-example/US-2",
    ]


def test_generator_ready_renders_end_to_end(generator_ready_json: Path, temp_output_dir: Path) -> None:
    """``generator-ready.json`` renders a valid PDF through the renamed ``technical-project`` template."""
    data = load_source(str(generator_ready_json))
    output_pdf = temp_output_dir / "generator-ready.pdf"

    html = _render(data, generator_ready_json, output_pdf)

    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0
    with open(output_pdf, "rb") as f:
        assert f.read(5) == b"%PDF-"

    # Content pulled from the nested envelope reaches the rendered HTML.
    assert "Generate PDF from a JSON source" in html
    assert "Override the built-in template" in html
    assert "Business Value" in html
    assert _item_count(generator_ready_json, data, output_pdf) == 2


def test_generator_ready_schema_version_key_is_inert(generator_ready_json: Path, temp_output_dir: Path) -> None:
    """The top-level ``schema_version`` key does not change the render output."""
    data = load_source(str(generator_ready_json))
    equivalent = copy.deepcopy(data)
    equivalent.pop("schema_version")

    with_dir = temp_output_dir / "with_version"
    without_dir = temp_output_dir / "without_version"
    with_dir.mkdir()
    without_dir.mkdir()

    meta = build_meta("Generator-Ready Golden", str(generator_ready_json)).to_dict()
    html_with_version = _render(data, generator_ready_json, with_dir / "out.pdf", meta=meta)
    html_without_version = _render(equivalent, generator_ready_json, without_dir / "out.pdf", meta=meta)

    assert html_with_version == html_without_version
