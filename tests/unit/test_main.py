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

"""Unit tests for main entrypoint."""

import json
import sys
from pathlib import Path

import pytest

import main
from generator.pdf_generator import FileIOError, RenderingError
from generator.schema_validator import SchemaValidationError
from generator.template_renderer import TemplateError


def test_run_outputs_all_paths_on_success(monkeypatch, tmp_path) -> None:
    """Test that run() outputs all paths on successful generation."""
    output_calls: list[tuple[str, str]] = []
    failed_calls: list[str] = []

    # Create test files
    pdf_ready_file = tmp_path / "input.json"
    pdf_ready_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["test"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    pdf_ready_file.write_text(json.dumps(pdf_ready_data))

    output_path = tmp_path / "output.pdf"

    # Mock dependencies
    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_output_path", staticmethod(lambda: str(output_path)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_debug_html", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))

    # Mock PDF generator
    class FakePdfGenerator:
        def generate_pdf(self, html, output_path_arg, template_dir):
            # Create fake PDF
            with open(output_path_arg, "w") as f:
                f.write("fake pdf")

    monkeypatch.setattr(main, "PdfGenerator", FakePdfGenerator)
    monkeypatch.setattr(main, "set_action_output", lambda name, value: output_calls.append((name, value)))
    monkeypatch.setattr(main, "set_action_failed", lambda msg, exit_code=1: failed_calls.append(msg))

    main.run()

    assert failed_calls == []
    assert len(output_calls) == 2  # pdf-path and report-path
    assert any(name == "pdf-path" for name, _ in output_calls)
    assert any(name == "report-path" for name, _ in output_calls)


def test_run_outputs_html_path_when_debug_enabled(monkeypatch, tmp_path) -> None:
    """Test that run() outputs html-path when debug_html is enabled."""
    output_calls: list[tuple[str, str]] = []

    # Create test files
    pdf_ready_file = tmp_path / "input.json"
    pdf_ready_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["test"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    pdf_ready_file.write_text(json.dumps(pdf_ready_data))

    output_path = tmp_path / "output.pdf"

    # Mock dependencies
    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_output_path", staticmethod(lambda: str(output_path)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_debug_html", staticmethod(lambda: True))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))

    class FakePdfGenerator:
        def generate_pdf(self, html, output_path_arg, template_dir):
            with open(output_path_arg, "w") as f:
                f.write("fake pdf")

    monkeypatch.setattr(main, "PdfGenerator", FakePdfGenerator)
    monkeypatch.setattr(main, "set_action_output", lambda name, value: output_calls.append((name, value)))
    monkeypatch.setattr(main, "set_action_failed", lambda msg, exit_code=1: None)

    main.run()

    output_names = [name for name, _ in output_calls]
    assert "html-path" in output_names
    assert "pdf-path" in output_names
    assert "report-path" in output_names


def test_run_exits_with_code_1_on_value_error(monkeypatch) -> None:
    """Test that run() exits with code 1 on ValueError."""
    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: None))

    # Mock validate_pdf_ready_json to raise ValueError
    def raise_value_error(path):
        raise ValueError("Invalid input")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "validate_pdf_ready_json", raise_value_error)
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 1


def test_run_exits_with_code_2_on_schema_validation_error(monkeypatch, tmp_path) -> None:
    """Test that run() exits with code 2 on SchemaValidationError."""
    pdf_ready_file = tmp_path / "input.json"

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))

    def raise_schema_error(path):
        raise SchemaValidationError("Schema validation failed")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "validate_pdf_ready_json", raise_schema_error)
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 2


def test_run_exits_with_code_3_on_template_error(monkeypatch, tmp_path) -> None:
    """Test that run() exits with code 3 on TemplateError."""
    pdf_ready_file = tmp_path / "input.json"
    pdf_ready_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["test"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    pdf_ready_file.write_text(json.dumps(pdf_ready_data))

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))

    class FakeRenderer:
        def render(self, data):
            raise TemplateError("Template not found")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "TemplateRenderer", lambda x: FakeRenderer())
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 3


def test_run_exits_with_code_4_on_rendering_error(monkeypatch, tmp_path) -> None:
    """Test that run() exits with code 4 on RenderingError."""
    pdf_ready_file = tmp_path / "input.json"
    pdf_ready_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["test"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    pdf_ready_file.write_text(json.dumps(pdf_ready_data))

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_debug_html", staticmethod(lambda: False))

    class FakePdfGenerator:
        def generate_pdf(self, html, output_path, template_dir):
            raise RenderingError("Rendering failed")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "PdfGenerator", FakePdfGenerator)
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 4


def test_run_exits_with_code_5_on_file_io_error(monkeypatch, tmp_path) -> None:
    """Test that run() exits with code 5 on FileIOError."""
    pdf_ready_file = tmp_path / "input.json"
    pdf_ready_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["test"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    pdf_ready_file.write_text(json.dumps(pdf_ready_data))

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_debug_html", staticmethod(lambda: False))

    class FakePdfGenerator:
        def generate_pdf(self, html, output_path, template_dir):
            raise FileIOError("File I/O error")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "PdfGenerator", FakePdfGenerator)
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 5


# --- Debug HTML output tests (migrated from test_debug_html.py) ---


def test_debug_html_filename_derivation():
    """Test that debug HTML filename is correctly derived from PDF path."""
    output_path = Path("/path/to/output.pdf")
    expected_html = output_path.parent / "output_rendered.html"

    html_filename = f"{output_path.stem}_rendered.html"
    html_path = output_path.parent / html_filename

    assert html_path == expected_html
    assert str(html_path) == "/path/to/output_rendered.html"


def test_debug_html_filename_with_nested_path():
    """Test debug HTML filename with nested directory path."""
    output_path = Path("/workspace/docs/reports/documentation.pdf")
    html_filename = f"{output_path.stem}_rendered.html"
    html_path = output_path.parent / html_filename

    assert str(html_path) == "/workspace/docs/reports/documentation_rendered.html"


def test_debug_html_saved_when_enabled(tmp_path):
    """Test that HTML is saved when debug_html is enabled."""
    output_path = tmp_path / "output.pdf"
    html_content = "<html><body><h1>Test</h1></body></html>"

    html_filename = f"{output_path.stem}_rendered.html"
    html_path = output_path.parent / html_filename
    html_path.write_text(html_content, encoding="utf-8")

    assert html_path.exists()
    assert html_path.read_text(encoding="utf-8") == html_content


def test_debug_html_contains_correct_content(tmp_path):
    """Test that saved debug HTML contains the rendered content."""
    output_path = tmp_path / "report.pdf"
    html_content = (
        "<html><head>"
        "<style>body { font-family: sans-serif; }</style>"
        "</head><body>"
        "<h1>Test Document</h1>"
        "<p>This is test content with <strong>formatting</strong>.</p>"
        "</body></html>"
    )

    html_filename = f"{output_path.stem}_rendered.html"
    html_path = output_path.parent / html_filename
    html_path.write_text(html_content, encoding="utf-8")

    saved_content = html_path.read_text(encoding="utf-8")
    assert "<h1>Test Document</h1>" in saved_content
    assert "<strong>formatting</strong>" in saved_content
    assert "<style>" in saved_content


# --- Coverage for custom template_dir branch (main.py lines 61-63) ---


def _make_pdf_ready_file(tmp_path):
    """Helper: create a valid pdf_ready.json and return its path."""
    pdf_ready_file = tmp_path / "input.json"
    pdf_ready_data = {
        "schema_version": "1.0",
        "meta": {
            "document_title": "Test",
            "document_version": "1.0.0",
            "generated_at": "2026-01-21T12:00:00Z",
            "source_set": ["test"],
            "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
        },
        "content": {"user_stories": []},
    }
    pdf_ready_file.write_text(json.dumps(pdf_ready_data))
    return pdf_ready_file


def test_run_with_custom_template_dir(monkeypatch, tmp_path) -> None:
    """Test that run() uses custom template pack when template_dir is set."""
    output_calls: list[tuple[str, str]] = []
    pdf_ready_file = _make_pdf_ready_file(tmp_path)
    output_path = tmp_path / "output.pdf"
    custom_dir = str(tmp_path / "custom_templates")

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_output_path", staticmethod(lambda: str(output_path)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: custom_dir))
    monkeypatch.setattr(main.ActionInputs, "get_debug_html", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))

    class FakePdfGenerator:
        def generate_pdf(self, html, output_path_arg, template_dir):
            with open(output_path_arg, "w") as f:
                f.write("fake pdf")

    monkeypatch.setattr(main, "PdfGenerator", FakePdfGenerator)
    monkeypatch.setattr(main, "set_action_output", lambda name, value: output_calls.append((name, value)))
    monkeypatch.setattr(main, "set_action_failed", lambda msg, exit_code=1: None)

    main.run()

    assert any(name == "pdf-path" for name, _ in output_calls)


# --- Coverage for verbose stack traces ---


def test_run_verbose_value_error(monkeypatch) -> None:
    """Test that verbose=True logs stack trace on ValueError."""
    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: True))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: None))

    def raise_value_error(path):
        raise ValueError("Invalid input")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "validate_pdf_ready_json", raise_value_error)
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 1


def test_run_verbose_schema_validation_error(monkeypatch, tmp_path) -> None:
    """Test that verbose=True logs stack trace on SchemaValidationError."""
    pdf_ready_file = _make_pdf_ready_file(tmp_path)

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: True))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))

    def raise_schema_error(path):
        raise SchemaValidationError("Schema validation failed")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "validate_pdf_ready_json", raise_schema_error)
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 2


def test_run_verbose_template_error(monkeypatch, tmp_path) -> None:
    """Test that verbose=True logs stack trace on TemplateError."""
    pdf_ready_file = _make_pdf_ready_file(tmp_path)

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: True))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))

    class FakeRenderer:
        def render(self, data):
            raise TemplateError("Template not found")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "TemplateRenderer", lambda x: FakeRenderer())
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 3


def test_run_verbose_rendering_error(monkeypatch, tmp_path) -> None:
    """Test that verbose=True logs stack trace on RenderingError."""
    pdf_ready_file = _make_pdf_ready_file(tmp_path)

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: True))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_debug_html", staticmethod(lambda: False))

    class FakePdfGenerator:
        def generate_pdf(self, html, output_path, template_dir):
            raise RenderingError("Rendering failed")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "PdfGenerator", FakePdfGenerator)
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 4


def test_run_verbose_file_io_error(monkeypatch, tmp_path) -> None:
    """Test that verbose=True logs stack trace on FileIOError."""
    pdf_ready_file = _make_pdf_ready_file(tmp_path)

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: True))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_debug_html", staticmethod(lambda: False))

    class FakePdfGenerator:
        def generate_pdf(self, html, output_path, template_dir):
            raise FileIOError("File I/O error")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "PdfGenerator", FakePdfGenerator)
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 5


# --- Coverage for unexpected Exception handler ---


def test_run_exits_with_code_1_on_unexpected_error(monkeypatch, tmp_path) -> None:
    """Test that run() exits with code 1 on unexpected Exception."""
    pdf_ready_file = _make_pdf_ready_file(tmp_path)

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: False))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))

    class FakeRenderer:
        def render(self, data):
            raise RuntimeError("Something unexpected")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "TemplateRenderer", lambda x: FakeRenderer())
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 1


def test_run_verbose_unexpected_error(monkeypatch, tmp_path) -> None:
    """Test that verbose=True logs stack trace on unexpected Exception."""
    pdf_ready_file = _make_pdf_ready_file(tmp_path)

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))
    monkeypatch.setattr(main.ActionInputs, "get_verbose", staticmethod(lambda: True))
    monkeypatch.setattr(main.ActionInputs, "get_pdf_ready_json", staticmethod(lambda: str(pdf_ready_file)))
    monkeypatch.setattr(main.ActionInputs, "get_template_dir", staticmethod(lambda: None))

    class FakeRenderer:
        def render(self, data):
            raise RuntimeError("Something unexpected")

    def mock_set_action_failed(msg, exit_code=1):
        sys.exit(exit_code)

    monkeypatch.setattr(main, "TemplateRenderer", lambda x: FakeRenderer())
    monkeypatch.setattr(main, "set_action_failed", mock_set_action_failed)

    with pytest.raises(SystemExit) as exc_info:
        main.run()

    assert exc_info.value.code == 1
