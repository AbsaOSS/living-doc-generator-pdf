import logging

import pytest

from generator.action_inputs import ActionInputs


def test_get_source_path_required(monkeypatch) -> None:
    """get_source_path raises ValueError when neither source-path nor alias is set."""
    monkeypatch.delenv("INPUT_SOURCE_PATH", raising=False)
    monkeypatch.delenv("INPUT_PDF_READY_JSON", raising=False)

    with pytest.raises(ValueError, match="source-path input is required"):
        ActionInputs.get_source_path()


def test_get_source_path_from_env(monkeypatch) -> None:
    """get_source_path reads source-path from environment."""
    monkeypatch.setenv("INPUT_SOURCE_PATH", "  data.json  ")
    assert ActionInputs.get_source_path() == "data.json"


def test_get_source_path_falls_back_to_deprecated_alias(monkeypatch, caplog) -> None:
    """get_source_path falls back to the deprecated pdf-ready-json alias with a warning."""
    monkeypatch.delenv("INPUT_SOURCE_PATH", raising=False)
    monkeypatch.setenv("INPUT_PDF_READY_JSON", "legacy.json")

    caplog.set_level(logging.WARNING)
    assert ActionInputs.get_source_path() == "legacy.json"
    assert "deprecated" in caplog.text.lower()


def test_get_template_path_optional(monkeypatch) -> None:
    """get_template_path returns None when not provided."""
    monkeypatch.delenv("INPUT_TEMPLATE_PATH", raising=False)
    assert ActionInputs.get_template_path() is None


def test_get_template_path_from_env(monkeypatch) -> None:
    """get_template_path reads and strips the value."""
    monkeypatch.setenv("INPUT_TEMPLATE_PATH", "  custom/templates  ")
    assert ActionInputs.get_template_path() == "custom/templates"


def test_get_document_type_optional(monkeypatch) -> None:
    """get_document_type returns None when not provided."""
    monkeypatch.delenv("INPUT_DOCUMENT_TYPE", raising=False)
    assert ActionInputs.get_document_type() is None


def test_get_document_type_from_env(monkeypatch) -> None:
    """get_document_type reads the value."""
    monkeypatch.setenv("INPUT_DOCUMENT_TYPE", "user-stories")
    assert ActionInputs.get_document_type() == "user-stories"


def test_get_schema_path_optional(monkeypatch) -> None:
    """get_schema_path returns None when not provided."""
    monkeypatch.delenv("INPUT_SCHEMA_PATH", raising=False)
    assert ActionInputs.get_schema_path() is None


def test_get_schema_path_from_env(monkeypatch) -> None:
    """get_schema_path reads the value."""
    monkeypatch.setenv("INPUT_SCHEMA_PATH", "schema.json")
    assert ActionInputs.get_schema_path() == "schema.json"


def test_get_output_path_default(monkeypatch) -> None:
    """get_output_path returns the default value."""
    monkeypatch.delenv("INPUT_OUTPUT_PATH", raising=False)
    assert ActionInputs.get_output_path() == "output.pdf"


def test_get_output_path_strips_whitespace(monkeypatch) -> None:
    """get_output_path strips whitespace."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "  my.pdf  ")
    assert ActionInputs.get_output_path() == "my.pdf"


def test_get_document_title_optional(monkeypatch) -> None:
    """get_document_title returns None when not provided."""
    monkeypatch.delenv("INPUT_DOCUMENT_TITLE", raising=False)
    assert ActionInputs.get_document_title() is None


def test_get_document_title_from_env(monkeypatch) -> None:
    """get_document_title reads and strips the value."""
    monkeypatch.setenv("INPUT_DOCUMENT_TITLE", "  My Title  ")
    assert ActionInputs.get_document_title() == "My Title"


def test_get_debug_html_boolean_variations(monkeypatch) -> None:
    """get_debug_html accepts various boolean formats."""
    test_cases = [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("", False),
        ("invalid", False),
    ]

    for input_value, expected in test_cases:
        monkeypatch.setenv("INPUT_DEBUG_HTML", input_value)
        assert ActionInputs.get_debug_html() == expected, f"Failed for input: {input_value}"


def test_get_verbose_with_runner_debug(monkeypatch) -> None:
    """get_verbose returns True when RUNNER_DEBUG is set."""
    monkeypatch.setenv("INPUT_VERBOSE", "false")
    monkeypatch.setenv("RUNNER_DEBUG", "1")
    assert ActionInputs.get_verbose() is True


def test_get_verbose_boolean_variations(monkeypatch) -> None:
    """get_verbose accepts various boolean formats."""
    monkeypatch.delenv("RUNNER_DEBUG", raising=False)

    test_cases = [
        ("true", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("", False),
    ]

    for input_value, expected in test_cases:
        monkeypatch.setenv("INPUT_VERBOSE", input_value)
        assert ActionInputs.get_verbose() == expected, f"Failed for input: {input_value}"


def test_validate_inputs_raises_on_blank_output_path(monkeypatch, caplog) -> None:
    """validate_inputs raises on blank output path."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "   ")

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError, match=r"Output path must be a non-empty string\."):
        ActionInputs.validate_inputs()

    assert "Output path must be a non-empty string." in caplog.text


def test_validate_inputs_requires_source_path(monkeypatch) -> None:
    """validate_inputs raises when source-path is missing."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "output.pdf")
    monkeypatch.delenv("INPUT_SOURCE_PATH", raising=False)
    monkeypatch.delenv("INPUT_PDF_READY_JSON", raising=False)

    with pytest.raises(ValueError, match="source-path input is required"):
        ActionInputs.validate_inputs()


def test_validate_inputs_requires_template_or_document_type(monkeypatch) -> None:
    """validate_inputs raises when neither template-path nor document-type is set."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "output.pdf")
    monkeypatch.setenv("INPUT_SOURCE_PATH", "data.json")
    monkeypatch.delenv("INPUT_TEMPLATE_PATH", raising=False)
    monkeypatch.delenv("INPUT_DOCUMENT_TYPE", raising=False)

    with pytest.raises(ValueError, match="Either template-path or document-type"):
        ActionInputs.validate_inputs()


def test_validate_inputs_rejects_unknown_document_type(monkeypatch) -> None:
    """validate_inputs raises when document-type is not a known built-in type."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "output.pdf")
    monkeypatch.setenv("INPUT_SOURCE_PATH", "data.json")
    monkeypatch.setenv("INPUT_DOCUMENT_TYPE", "nonsense")

    with pytest.raises(ValueError, match="Invalid document-type 'nonsense'"):
        ActionInputs.validate_inputs()


def test_validate_inputs_accepts_document_type(monkeypatch) -> None:
    """validate_inputs passes for a valid document-type."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "output.pdf")
    monkeypatch.setenv("INPUT_SOURCE_PATH", "data.json")
    monkeypatch.setenv("INPUT_DOCUMENT_TYPE", "user-stories")

    ActionInputs.validate_inputs()


def test_validate_inputs_accepts_template_path(monkeypatch) -> None:
    """validate_inputs passes when only template-path is provided."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "output.pdf")
    monkeypatch.setenv("INPUT_SOURCE_PATH", "data.json")
    monkeypatch.setenv("INPUT_TEMPLATE_PATH", "custom/templates")

    ActionInputs.validate_inputs()
