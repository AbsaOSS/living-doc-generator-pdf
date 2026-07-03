import pytest

import main
from generator.pdf_generator import FileIOError, RenderingError
from generator.schema_validator import SchemaValidationError
from generator.template_renderer import TemplateError


@pytest.fixture
def base_env(monkeypatch, tmp_path):
    """Configure a minimal valid environment for run()."""
    source = tmp_path / "data.json"
    source.write_text('{"items": []}', encoding="utf-8")
    output = tmp_path / "out.pdf"
    monkeypatch.setenv("INPUT_SOURCE_PATH", str(source))
    monkeypatch.setenv("INPUT_DOCUMENT_TYPE", "user-stories")
    monkeypatch.setenv("INPUT_OUTPUT_PATH", str(output))
    monkeypatch.delenv("INPUT_VERBOSE", raising=False)
    return {"source": str(source), "output": str(output)}


def test_resolve_document_title_uses_input(monkeypatch) -> None:
    """Explicit document-title input wins."""
    monkeypatch.setenv("INPUT_DOCUMENT_TITLE", "Custom")
    assert main._resolve_document_title("user-stories", "x.json") == "Custom"


def test_resolve_document_title_uses_type_default(monkeypatch) -> None:
    """Falls back to the built-in default title for the document type."""
    monkeypatch.delenv("INPUT_DOCUMENT_TITLE", raising=False)
    assert main._resolve_document_title("user-stories", "x.json") == "User Stories"


def test_resolve_document_title_uses_source_stem(monkeypatch) -> None:
    """Falls back to the source file stem when nothing else is available."""
    monkeypatch.delenv("INPUT_DOCUMENT_TITLE", raising=False)
    assert main._resolve_document_title(None, "/path/to/my-data.json") == "my-data"


def test_run_success(base_env, mocker) -> None:
    """A successful run sets the pdf-path output and does not fail."""
    renderer = mocker.Mock()
    renderer.render.return_value = "<html></html>"
    renderer.base_dir = "/tmp"
    mocker.patch("main.TemplateRenderer", return_value=renderer)
    mocker.patch("main.PdfGenerator").return_value.generate_pdf = mocker.Mock()
    mocker.patch("main.generate_pdf_report", return_value="pdf_report.json")
    set_output = mocker.patch("main.set_action_output")
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_not_called()
    output_keys = [call.args[0] for call in set_output.call_args_list]
    assert "pdf-path" in output_keys
    assert "report-path" in output_keys


def test_run_value_error_exit_code_1(base_env, mocker) -> None:
    """A ValueError maps to exit code 1."""
    mocker.patch("main.load_source", side_effect=ValueError("bad input"))
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("bad input", exit_code=1)


def test_run_schema_error_exit_code_2(base_env, mocker) -> None:
    """A SchemaValidationError maps to exit code 2."""
    mocker.patch("main.load_source", side_effect=SchemaValidationError("schema bad"))
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("schema bad", exit_code=2)


def test_run_template_error_exit_code_3(base_env, mocker) -> None:
    """A TemplateError maps to exit code 3."""
    mocker.patch("main.load_source", return_value={"items": []})
    mocker.patch("main.TemplateRenderer", side_effect=TemplateError("template bad"))
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("template bad", exit_code=3)


def test_run_rendering_error_exit_code_4(base_env, mocker) -> None:
    """A RenderingError maps to exit code 4."""
    mocker.patch("main.load_source", return_value={"items": []})
    renderer = mocker.Mock()
    renderer.render.return_value = "<html></html>"
    renderer.base_dir = "/tmp"
    mocker.patch("main.TemplateRenderer", return_value=renderer)
    pdf = mocker.patch("main.PdfGenerator").return_value
    pdf.generate_pdf.side_effect = RenderingError("render bad")
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("render bad", exit_code=4)


def test_run_file_io_error_exit_code_5(base_env, mocker) -> None:
    """A FileIOError maps to exit code 5."""
    mocker.patch("main.load_source", return_value={"items": []})
    renderer = mocker.Mock()
    renderer.render.return_value = "<html></html>"
    renderer.base_dir = "/tmp"
    mocker.patch("main.TemplateRenderer", return_value=renderer)
    pdf = mocker.patch("main.PdfGenerator").return_value
    pdf.generate_pdf.side_effect = FileIOError("io bad")
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("io bad", exit_code=5)


def test_run_unexpected_error_exit_code_1(base_env, mocker) -> None:
    """An unexpected exception maps to exit code 1 with a prefixed message."""
    mocker.patch("main.load_source", side_effect=RuntimeError("boom"))
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("Unexpected error: boom", exit_code=1)
