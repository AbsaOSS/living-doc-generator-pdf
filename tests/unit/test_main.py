import json

import pytest

import main
from generator.pdf_generator import FileIOError, RenderingError
from generator.schema_validator import SchemaValidationError
from generator.template_renderer import TemplateError


@pytest.fixture
def base_env(monkeypatch, tmp_path):
    """Configure a minimal valid environment for run()."""
    source = tmp_path / "data.json"
    source.write_text(
        json.dumps(
            {
                "schema_version": "generator-ready-v1.0.0",
                "meta": {
                    "document_title": "T",
                    "document_version": "1.0.0",
                    "generated_at": "2024-01-01T00:00:00Z",
                    "source_set": ["github:x/y"],
                    "selection_summary": {"total_items": 0, "included_items": 0, "excluded_items": 0},
                },
                "content": {"user_stories": []},
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "out.pdf"
    monkeypatch.setenv("INPUT_SOURCE_PATH", str(source))
    monkeypatch.setenv("INPUT_DOCUMENT_TYPE", "technical-project")
    monkeypatch.setenv("INPUT_OUTPUT_PATH", str(output))
    monkeypatch.delenv("INPUT_VERBOSE", raising=False)
    return {"source": str(source), "output": str(output)}


def test_resolve_document_title_uses_input(monkeypatch) -> None:
    """Explicit document-title input wins."""
    monkeypatch.setenv("INPUT_DOCUMENT_TITLE", "Custom")
    assert main._resolve_document_title("technical-project", "x.json") == "Custom"


def test_resolve_document_title_uses_type_default(monkeypatch) -> None:
    """Falls back to the built-in default title for the document type."""
    monkeypatch.delenv("INPUT_DOCUMENT_TITLE", raising=False)
    assert main._resolve_document_title("technical-project", "x.json") == "Technical Project"


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
    mocker.patch("main.load_json", side_effect=ValueError("bad input"))
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("bad input", exit_code=1)


def test_run_schema_error_exit_code_2(base_env, monkeypatch, tmp_path, mocker) -> None:
    """A SchemaValidationError from optional structural validation maps to exit code 2."""
    monkeypatch.setenv("INPUT_SCHEMA_PATH", str(tmp_path / "schema.json"))
    mocker.patch("main.load_json", return_value={"schema_version": "generator-ready-v1.0.0", "meta": {}, "content": {"user_stories": []}})
    mocker.patch("main.validate_source", side_effect=SchemaValidationError("schema bad"))
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("schema bad", exit_code=2)


def test_run_template_error_exit_code_3(base_env, mocker) -> None:
    """A TemplateError maps to exit code 3."""
    mocker.patch("main.load_json", return_value={"schema_version": "generator-ready-v1.0.0", "meta": {}, "content": {"user_stories": []}})
    mocker.patch("main.validate_source")
    mocker.patch("main.TemplateRenderer", side_effect=TemplateError("template bad"))
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("template bad", exit_code=3)


def test_run_rendering_error_exit_code_4(base_env, mocker) -> None:
    """A RenderingError maps to exit code 4."""
    mocker.patch("main.load_json", return_value={"schema_version": "generator-ready-v1.0.0", "meta": {}, "content": {"user_stories": []}})
    renderer = mocker.Mock()
    renderer.render.return_value = "<html></html>"
    renderer.base_dir = "/tmp"
    mocker.patch("main.validate_source")
    mocker.patch("main.TemplateRenderer", return_value=renderer)
    pdf = mocker.patch("main.PdfGenerator").return_value
    pdf.generate_pdf.side_effect = RenderingError("render bad")
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("render bad", exit_code=4)


def test_run_file_io_error_exit_code_5(base_env, mocker) -> None:
    """A FileIOError maps to exit code 5."""
    mocker.patch("main.load_json", return_value={"schema_version": "generator-ready-v1.0.0", "meta": {}, "content": {"user_stories": []}})
    renderer = mocker.Mock()
    renderer.render.return_value = "<html></html>"
    renderer.base_dir = "/tmp"
    mocker.patch("main.validate_source")
    mocker.patch("main.TemplateRenderer", return_value=renderer)
    pdf = mocker.patch("main.PdfGenerator").return_value
    pdf.generate_pdf.side_effect = FileIOError("io bad")
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("io bad", exit_code=5)


def test_run_out_of_range_schema_version_still_renders(base_env, mocker) -> None:
    """An out-of-range schema_version warns but still renders and passes the warning through."""
    mocker.patch("main.load_json", return_value={"schema_version": "generator-ready-v2.0.0", "meta": {}, "content": {"user_stories": []}})
    renderer = mocker.Mock()
    renderer.render.return_value = "<html></html>"
    renderer.base_dir = "/tmp"
    mocker.patch("main.TemplateRenderer", return_value=renderer)
    generate_pdf = mocker.patch("main.PdfGenerator").return_value.generate_pdf
    report = mocker.patch("main.generate_pdf_report", return_value="pdf_report.json")
    mocker.patch("main.set_action_output")
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_not_called()
    renderer.render.assert_called_once()
    generate_pdf.assert_called_once()
    warnings = report.call_args.kwargs["warnings"]
    assert warnings
    assert warnings[0]["code"] == "schema_version_out_of_range"


def test_run_out_of_range_skips_structural_validation(base_env, monkeypatch, tmp_path, mocker, caplog) -> None:
    """An out-of-range schema_version renders best-effort: structural validation is skipped
    so a schema pinning the version (const) cannot pre-empt the warn-and-render path, and the
    step log states the real reason (not the misleading 'No schema-path provided')."""
    monkeypatch.setenv("INPUT_SCHEMA_PATH", str(tmp_path / "schema.json"))
    mocker.patch("main.load_json", return_value={"schema_version": "coverage-matrix-v2.0.0", "meta": {}, "content": {"user_stories": []}})
    renderer = mocker.Mock()
    renderer.render.return_value = "<html></html>"
    renderer.base_dir = "/tmp"
    mocker.patch("main.TemplateRenderer", return_value=renderer)
    generate_pdf = mocker.patch("main.PdfGenerator").return_value.generate_pdf
    validate_source = mocker.patch("main.validate_source")
    mocker.patch("main.generate_pdf_report", return_value="pdf_report.json")
    mocker.patch("main.set_action_output")
    set_failed = mocker.patch("main.set_action_failed")

    with caplog.at_level("INFO"):
        main.run()

    set_failed.assert_not_called()
    validate_source.assert_not_called()
    generate_pdf.assert_called_once()
    messages = [r.message for r in caplog.records]
    assert any("outside the supported range" in m and "best-effort" in m for m in messages)
    assert not any("No schema-path provided" in m for m in messages)


def test_run_no_schema_path_logs_skip_step(base_env, monkeypatch, mocker, caplog) -> None:
    """A document type without a default schema still emits the canonical 'skipping validation' step log."""
    monkeypatch.setenv("INPUT_DOCUMENT_TYPE", "ui-test-catalog")
    mocker.patch("main.load_json", return_value={"schema_version": "generator-ready-v1.0.0", "meta": {}, "content": {"user_stories": []}})
    renderer = mocker.Mock()
    renderer.render.return_value = "<html></html>"
    renderer.base_dir = "/tmp"
    mocker.patch("main.TemplateRenderer", return_value=renderer)
    mocker.patch("main.PdfGenerator").return_value.generate_pdf = mocker.Mock()
    mocker.patch("main.generate_pdf_report", return_value="pdf_report.json")
    mocker.patch("main.set_action_output")

    with caplog.at_level("INFO"):
        main.run()

    assert any("skipping validation" in r.message for r in caplog.records)


def test_run_unparseable_schema_version_exit_code_1(base_env, mocker) -> None:
    """A present-but-unparseable schema_version maps to exit code 1."""
    mocker.patch("main.load_json", return_value={"schema_version": "generator-ready", "meta": {}, "content": {"user_stories": []}})
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once()
    message = set_failed.call_args.args[0]
    assert message.startswith("Invalid input:")
    assert "schema_version" in message
    assert set_failed.call_args.kwargs["exit_code"] == 1


def test_run_missing_schema_version_exit_code_1(base_env, mocker) -> None:
    """An input with no schema_version fails with one structured message (exit code 1)."""
    mocker.patch("main.load_json", return_value={"meta": {}, "content": {"user_stories": []}})
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once()
    message = set_failed.call_args.args[0]
    assert message.startswith("Invalid input:")
    assert "schema_version" in message
    assert set_failed.call_args.kwargs["exit_code"] == 1


def test_resolve_schema_path_explicit_wins() -> None:
    """An explicit schema-path is used verbatim and never flagged as the default."""
    assert main._resolve_schema_path("technical-project", "custom.json") == ("custom.json", False)


def test_resolve_schema_path_defaults_for_technical_project() -> None:
    """technical-project with no schema-path defaults to the vendored generator-ready schema."""
    path, is_default = main._resolve_schema_path("technical-project", None)
    assert is_default is True
    assert path.endswith("generator-ready-v1.0.0-schema.json")


def test_resolve_schema_path_opt_in_for_other_types() -> None:
    """Other document types keep validation opt-in."""
    assert main._resolve_schema_path("ui-test-catalog", None) == (None, False)


def test_run_raw_collector_source_rejected_with_normalization_hint(base_env, mocker) -> None:
    """A raw collector file under the defaulted technical-project schema fails, pointing at normalization."""
    mocker.patch(
        "main.load_json",
        return_value={"schema_version": "generator-ready-v1.0.0", "user_stories": [], "features": []},
    )
    validate_source = mocker.patch("main.validate_source")
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    validate_source.assert_not_called()
    message, kwargs = set_failed.call_args.args[0], set_failed.call_args.kwargs
    assert kwargs["exit_code"] == 2
    assert "normalization" in message
    assert message.startswith("Schema validation failed:")


def test_run_raw_collector_source_rejected_even_when_schema_version_out_of_range(base_env, mocker) -> None:
    """The raw-collector guard is a hard guarantee: an out-of-range schema_version still
    cannot smuggle raw collector output past the defaulted technical-project schema."""
    mocker.patch(
        "main.load_json",
        return_value={"schema_version": "generator-ready-v2.0.0", "user_stories": [], "features": []},
    )
    validate_source = mocker.patch("main.validate_source")
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    validate_source.assert_not_called()
    message, kwargs = set_failed.call_args.args[0], set_failed.call_args.kwargs
    assert kwargs["exit_code"] == 2
    assert message.startswith("Schema validation failed:")
    assert "normalization" in message


def test_run_normalized_source_runs_structural_validation(base_env, mocker) -> None:
    """A normalized envelope passes the raw-collector guard and reaches structural validation."""
    mocker.patch(
        "main.load_json",
        return_value={"schema_version": "generator-ready-v1.0.0", "meta": {}, "content": {"user_stories": []}},
    )
    validate_source = mocker.patch("main.validate_source")
    renderer = mocker.Mock()
    renderer.render.return_value = "<html></html>"
    renderer.base_dir = "/tmp"
    mocker.patch("main.TemplateRenderer", return_value=renderer)
    mocker.patch("main.PdfGenerator").return_value.generate_pdf = mocker.Mock()
    mocker.patch("main.generate_pdf_report", return_value="pdf_report.json")
    mocker.patch("main.set_action_output")
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_not_called()
    validate_source.assert_called_once()
    assert validate_source.call_args.args[1].endswith("generator-ready-v1.0.0-schema.json")


def test_run_unexpected_error_exit_code_1(base_env, mocker) -> None:
    """An unexpected exception maps to exit code 1 with a prefixed message."""
    mocker.patch("main.load_json", side_effect=RuntimeError("boom"))
    set_failed = mocker.patch("main.set_action_failed")

    main.run()

    set_failed.assert_called_once_with("Unexpected error: boom", exit_code=1)
