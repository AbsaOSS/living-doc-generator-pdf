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


def _render(data: dict, source: Path, output_pdf: Path, meta: dict | None = None) -> str:
    renderer = TemplateRenderer(document_type="user-stories")
    if meta is None:
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

    # Reuse one meta so both renders share the same generated_at and stay comparable.
    meta = build_meta("Generator-Ready Regression", str(generator_ready_json)).to_dict()
    html_with_version = _render(data, generator_ready_json, with_version_pdf, meta=meta)
    html_without_version = _render(equivalent, generator_ready_json, without_version_pdf, meta=meta)

    assert html_with_version == html_without_version

    count_with = _item_count(generator_ready_json, data, with_version_pdf)
    count_without = _item_count(generator_ready_json, equivalent, without_version_pdf)

    assert count_with == count_without == len(data["user_stories"])


def test_generator_ready_matches_user_stories_baseline(
    generator_ready_json: Path, user_stories_json: Path, temp_output_dir: Path
) -> None:
    """The renamed artifact renders identically to the equivalent ``user_stories.json`` baseline.

    ``examples/generator-ready.json`` is a trimmed copy of ``examples/user_stories.json``
    (same two user stories, plus the new ``schema_version``). Rendering the matching subset
    of the ``user_stories.json`` baseline must produce the same HTML and item count as
    rendering the renamed artifact, proving the rename carries no behavioural change.
    """
    generator_ready_data = load_source(str(generator_ready_json))
    equivalent = copy.deepcopy(generator_ready_data)
    equivalent.pop("schema_version")

    baseline_data = load_source(str(user_stories_json))
    baseline_ids = {story["id"] for story in equivalent["user_stories"]}
    baseline_subset = copy.deepcopy(baseline_data)
    baseline_subset["user_stories"] = [
        story for story in baseline_subset["user_stories"] if story["id"] in baseline_ids
    ]

    assert baseline_subset["user_stories"] == equivalent["user_stories"]

    generator_ready_dir = temp_output_dir / "generator_ready"
    baseline_dir = temp_output_dir / "baseline"
    generator_ready_dir.mkdir()
    baseline_dir.mkdir()
    generator_ready_pdf = generator_ready_dir / "out.pdf"
    baseline_pdf = baseline_dir / "out.pdf"

    # Reuse one meta so both renders share the same generated_at and stay comparable.
    meta = build_meta("Generator-Ready Regression", str(generator_ready_json)).to_dict()
    html_generator_ready = _render(equivalent, generator_ready_json, generator_ready_pdf, meta=meta)
    html_baseline = _render(baseline_subset, user_stories_json, baseline_pdf, meta=meta)

    assert html_generator_ready == html_baseline

    count_generator_ready = _item_count(generator_ready_json, equivalent, generator_ready_pdf)
    count_baseline = _item_count(user_stories_json, baseline_subset, baseline_pdf)

    assert count_generator_ready == count_baseline == len(equivalent["user_stories"])
