import logging

import pytest

from generator.action_inputs import ActionInputs


def test_get_pdf_ready_json_required(monkeypatch) -> None:
    """Test that get_pdf_ready_json raises ValueError when missing."""
    monkeypatch.delenv("INPUT_PDF_READY_JSON", raising=False)

    with pytest.raises(ValueError, match="pdf_ready_json input is required"):
        ActionInputs.get_pdf_ready_json()


def test_get_pdf_ready_json_from_env(monkeypatch) -> None:
    """Test that get_pdf_ready_json reads from environment."""
    monkeypatch.setenv("INPUT_PDF_READY_JSON", "path/to/data.json")
    assert ActionInputs.get_pdf_ready_json() == "path/to/data.json"


def test_get_output_path_default(monkeypatch) -> None:
    """Test that get_output_path returns default value."""
    monkeypatch.delenv("INPUT_OUTPUT_PATH", raising=False)
    assert ActionInputs.get_output_path() == "output.pdf"


def test_get_output_path_strips_whitespace(monkeypatch) -> None:
    """Test that get_output_path strips whitespace."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "  my.pdf  ")
    assert ActionInputs.get_output_path() == "my.pdf"


def test_get_template_dir_optional(monkeypatch) -> None:
    """Test that get_template_dir returns None when not provided."""
    monkeypatch.delenv("INPUT_TEMPLATE_DIR", raising=False)
    assert ActionInputs.get_template_dir() is None


def test_get_template_dir_from_env(monkeypatch) -> None:
    """Test that get_template_dir reads from environment."""
    monkeypatch.setenv("INPUT_TEMPLATE_DIR", "custom/templates")
    assert ActionInputs.get_template_dir() == "custom/templates"


def test_get_template_path_returns_none_when_empty(monkeypatch) -> None:
    """Test that get_template_path returns None when empty (deprecated)."""
    monkeypatch.setenv("INPUT_TEMPLATE_PATH", "")
    assert ActionInputs.get_template_path() is None


def test_get_debug_html_boolean_variations(monkeypatch) -> None:
    """Test that get_debug_html accepts various boolean formats."""
    test_cases = [
        ("true", True),
        ("TRUE", True),
        ("True", True),
        ("1", True),
        ("yes", True),
        ("YES", True),
        ("false", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("NO", False),
        ("", False),
        ("invalid", False),
    ]

    for input_value, expected in test_cases:
        monkeypatch.setenv("INPUT_DEBUG_HTML", input_value)
        assert ActionInputs.get_debug_html() == expected, f"Failed for input: {input_value}"


def test_get_verbose_with_runner_debug(monkeypatch) -> None:
    """Test that get_verbose returns True when RUNNER_DEBUG is set."""
    monkeypatch.setenv("INPUT_VERBOSE", "false")
    monkeypatch.setenv("RUNNER_DEBUG", "1")
    assert ActionInputs.get_verbose() is True


def test_get_verbose_boolean_variations(monkeypatch) -> None:
    """Test that get_verbose accepts various boolean formats."""
    monkeypatch.delenv("RUNNER_DEBUG", raising=False)

    test_cases = [
        ("true", True),
        ("TRUE", True),
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
    """Test that validate_inputs raises on blank output path."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "   ")

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError, match="Output path must be a non-empty string"):
        ActionInputs.validate_inputs()

    assert "Output path must be a non-empty string." in caplog.text


def test_validate_inputs_missing_required(monkeypatch) -> None:
    """Test that validate_inputs handles missing pdf_ready_json during transition."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "output.pdf")
    monkeypatch.delenv("INPUT_PDF_READY_JSON", raising=False)

    # Should not raise during transition period
    ActionInputs.validate_inputs()
