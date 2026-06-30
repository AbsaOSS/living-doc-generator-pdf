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

"""Integration tests for error handling scenarios and exit-code mapping."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from generator.models import build_meta
from generator.pdf_generator import FileIOError, PdfGenerator
from generator.schema_validator import SchemaValidationError, load_source
from generator.template_renderer import TemplateError, TemplateRenderer


def test_source_file_not_found() -> None:
    """A missing source file raises ValueError (exit code 1)."""
    with pytest.raises(ValueError, match="not found"):
        load_source("/tmp/nonexistent_file.json")


def test_invalid_json_syntax(temp_output_dir: Path) -> None:
    """Invalid JSON syntax raises ValueError (exit code 1)."""
    bad = temp_output_dir / "invalid_syntax.json"
    bad.write_text("{invalid json syntax", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON"):
        load_source(str(bad))


def test_schema_validation_failure(temp_output_dir: Path, schemas_dir: Path) -> None:
    """Data that violates the schema raises SchemaValidationError (exit code 2)."""
    source = temp_output_dir / "bad_contract.json"
    source.write_text('{"not_items": []}', encoding="utf-8")
    schema = schemas_dir / "doc-issues-v1.0.0-schema.json"

    with pytest.raises(SchemaValidationError, match="Schema validation failed"):
        load_source(str(source), str(schema))


def test_schema_file_not_found(user_stories_json: Path) -> None:
    """A missing schema file raises ValueError (exit code 1)."""
    with pytest.raises(ValueError, match="Schema file"):
        load_source(str(user_stories_json), "/tmp/nonexistent_schema.json")


def test_missing_template_raises(temp_output_dir: Path) -> None:
    """Rendering with a directory lacking main.html.jinja raises TemplateError (exit code 3)."""
    empty_dir = temp_output_dir / "empty_templates"
    empty_dir.mkdir(exist_ok=True)
    renderer = TemplateRenderer(template_path=str(empty_dir))

    with pytest.raises(TemplateError, match="not found"):
        renderer.render({}, build_meta("T", "x.json").to_dict())


def test_template_syntax_error_raises(temp_output_dir: Path) -> None:
    """A template syntax error raises TemplateError (exit code 3)."""
    bad_dir = temp_output_dir / "bad_templates"
    bad_dir.mkdir(exist_ok=True)
    (bad_dir / "main.html.jinja").write_text("{% for x in %}", encoding="utf-8")
    renderer = TemplateRenderer(template_path=str(bad_dir))

    with pytest.raises(TemplateError, match="Syntax error"):
        renderer.render({}, build_meta("T", "x.json").to_dict())


def test_file_io_error_readonly_directory(minimal_json: Path, temp_output_dir: Path) -> None:
    """Writing to a read-only directory raises FileIOError (exit code 5)."""
    if sys.platform == "win32":
        pytest.skip("Permission semantics differ on Windows")

    readonly_dir = temp_output_dir / "readonly"
    readonly_dir.mkdir(exist_ok=True)
    os.chmod(readonly_dir, 0o444)

    try:
        data = load_source(str(minimal_json))
        renderer = TemplateRenderer(document_type="user-stories")
        html = renderer.render(data, build_meta("T", str(minimal_json)).to_dict())
        output_pdf = readonly_dir / "output.pdf"

        with pytest.raises(FileIOError, match="Failed to write PDF"):
            PdfGenerator().generate_pdf(html, str(output_pdf), renderer.base_dir)
    finally:
        os.chmod(readonly_dir, 0o755)
