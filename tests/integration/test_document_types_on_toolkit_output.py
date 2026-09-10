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

"""Golden tests: every built-in ``document-type`` validates a real ``toolkit``-produced
input against its vendored schema by default, then renders a valid PDF.

Each built-in type resolves a vendored schema with no explicit ``schema-path``
(``_resolve_schema_path``), the shipped ``examples/`` file is the canonical
producer output for that ``document-type``, and the render reaches a real PDF.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import main
from generator.models import build_meta
from generator.pdf_generator import PdfGenerator
from generator.schema_validator import SchemaValidationError, load_json, validate_source
from generator.template_renderer import TemplateRenderer


@pytest.mark.parametrize(
    "document_type, fixture_name, schema_filename",
    [
        ("technical-project", "generator_ready_json", "generator-ready-v1.0.0-schema.json"),
        ("ui-test-catalog", "ui_tests_json", "ui-tests-v1.0.0-schema.json"),
        ("coverage-matrix", "coverage_matrix_json", "coverage-matrix-v1.0.0-schema.json"),
    ],
)
def test_document_type_defaults_to_vendored_schema(
    request, document_type: str, fixture_name: str, schema_filename: str
) -> None:
    """With no ``schema-path``, each built-in type resolves and validates against
    its own vendored schema."""
    source: Path = request.getfixturevalue(fixture_name)

    schema_path, _ = main._resolve_schema_path(document_type, None)

    assert schema_path is not None
    assert Path(schema_path).name == schema_filename
    # Real producer output validates cleanly against the vendored schema.
    validate_source(load_json(str(source)), schema_path, str(source))


@pytest.mark.parametrize(
    "document_type, fixture_name, expected_markers",
    [
        (
            "ui-test-catalog",
            "ui_tests_json",
            ["Render a PDF from a valid source", "Unlinked Scenarios"],
        ),
        (
            "coverage-matrix",
            "coverage_matrix_json",
            ["Coverage Summary", "Generate PDF from a JSON source", "66.7%"],
        ),
    ],
)
def test_document_type_renders_toolkit_output_end_to_end(
    request, document_type: str, fixture_name: str, expected_markers: list[str], temp_output_dir: Path
) -> None:
    """The ``toolkit``-produced input renders to a real PDF through the built-in template set."""
    source: Path = request.getfixturevalue(fixture_name)
    data = load_json(str(source))

    renderer = TemplateRenderer(document_type=document_type)
    meta = build_meta("Golden", str(source)).to_dict()
    html = renderer.render(data, meta)

    output_pdf = temp_output_dir / f"{document_type}.pdf"
    PdfGenerator().generate_pdf(html, str(output_pdf), renderer.base_dir)

    assert output_pdf.read_bytes()[:5] == b"%PDF-"
    for marker in expected_markers:
        assert marker in html


@pytest.mark.parametrize(
    "document_type, fixture_name",
    [
        ("technical-project", "generator_ready_json"),
        ("ui-test-catalog", "ui_tests_json"),
        ("coverage-matrix", "coverage_matrix_json"),
    ],
)
def test_load_and_check_source_accepts_unmodified_producer_output(
    request, document_type: str, fixture_name: str
) -> None:
    """The real entrypoint path (``_load_and_check_source``) accepts each shipped
    producer artifact as-is — including ``ui-tests.json``, which carries no
    top-level ``schema_version``."""
    source: Path = request.getfixturevalue(fixture_name)
    schema_path, envelope = main._resolve_schema_path(document_type, None)

    data, warnings = main._load_and_check_source(str(source), schema_path, envelope, document_type)

    assert data
    assert warnings == []


def test_ui_test_catalog_rejects_structurally_invalid_source(ui_tests_json: Path, tmp_path: Path) -> None:
    """A ``ui-tests.json`` missing a required top-level key fails default validation."""
    data = load_json(str(ui_tests_json))
    data.pop("metadata")
    broken = tmp_path / "broken-ui-tests.json"
    broken.write_text(json.dumps(data), encoding="utf-8")

    schema_path, _ = main._resolve_schema_path("ui-test-catalog", None)
    with pytest.raises(SchemaValidationError):
        validate_source(load_json(str(broken)), schema_path, str(broken))
