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

"""Regression check: ``generator-pdf`` still renders ``toolkit``'s renamed output.

Phase 1 of the roadmap renamed the canonical dataset ``pdf_ready.json`` ->
``generator-ready.json`` and re-stamped its ``schema_version`` from ``"1.0"`` to
``"generator-ready-v1.0.0"``. ``generator-pdf`` consumes that file through its
generic ``source-path`` input and never keys on the filename or the
``schema_version`` string, so the rename should be transparent. These tests prove
it for today's (flat) render path. Wiring ``generator-pdf`` onto the canonical
nested schema is a later phase and is out of scope here.
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


def _render(data: dict, source: Path, output_pdf: Path) -> str:
    renderer = TemplateRenderer(document_type="user-stories")
    meta = build_meta("Generator-Ready Regression", str(source)).to_dict()
    html = renderer.render(data, meta)
    PdfGenerator().generate_pdf(html, str(output_pdf), renderer.base_dir)
    return html


def _item_count(source: Path, data: dict, output_pdf: Path) -> int:
    report_path = generate_pdf_report(
        input_file=str(source),
        output_file=str(output_pdf),
        template_pack_type="built-in",
        template_pack_path="user-stories",
        data=data,
        pdf_path=str(output_pdf),
        errors=[],
        warnings=[],
    )
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    return report["statistics"]["item_count"]


def test_generator_ready_renders_end_to_end(generator_ready_json: Path, temp_output_dir: Path) -> None:
    """A file named ``generator-ready.json`` renders a valid PDF through the generator."""
    data = load_source(str(generator_ready_json))
    output_pdf = temp_output_dir / "generator-ready.pdf"

    _render(data, generator_ready_json, output_pdf)

    assert output_pdf.exists()
    assert output_pdf.stat().st_size > 0
    with open(output_pdf, "rb") as f:
        assert f.read(5) == b"%PDF-"


def test_generator_ready_schema_version_is_read_back(generator_ready_json: Path) -> None:
    """The new ``schema_version`` string survives loading verbatim."""
    data = load_source(str(generator_ready_json))

    assert data["schema_version"] == "generator-ready-v1.0.0"


def test_generator_ready_schema_version_key_is_inert(generator_ready_json: Path, temp_output_dir: Path) -> None:
    """The extra top-level ``schema_version`` key does not change the render.

    Rendering the example and rendering the same payload with ``schema_version``
    stripped must produce byte-identical HTML and the same reported item count,
    proving the renamed artifact is consumed on today's path without a code
    change.
    """
    data = load_source(str(generator_ready_json))
    equivalent = copy.deepcopy(data)
    equivalent.pop("schema_version")

    with_dir = temp_output_dir / "with_version"
    without_dir = temp_output_dir / "without_version"
    with_dir.mkdir()
    without_dir.mkdir()
    with_version_pdf = with_dir / "out.pdf"
    without_version_pdf = without_dir / "out.pdf"

    html_with_version = _render(data, generator_ready_json, with_version_pdf)
    html_without_version = _render(equivalent, generator_ready_json, without_version_pdf)

    assert html_with_version == html_without_version

    count_with = _item_count(generator_ready_json, data, with_version_pdf)
    count_without = _item_count(generator_ready_json, equivalent, without_version_pdf)

    assert count_with == count_without == len(data["user_stories"])
