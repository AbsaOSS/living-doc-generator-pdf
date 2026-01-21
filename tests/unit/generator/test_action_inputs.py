import logging

import pytest

from generator.action_inputs import ActionInputs


def test_get_output_path_defaults_when_missing(monkeypatch) -> None:
    monkeypatch.delenv("INPUT_OUTPUT_PATH", raising=False)
    assert ActionInputs.get_output_path() == "output.pdf"


def test_get_output_path_strips_whitespace(monkeypatch) -> None:
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "  my.pdf  ")
    assert ActionInputs.get_output_path() == "my.pdf"


def test_get_template_path_returns_none_when_empty(monkeypatch) -> None:
    monkeypatch.setenv("INPUT_TEMPLATE_PATH", "")
    assert ActionInputs.get_template_path() is None


def test_get_verbose_true_when_runner_debug(monkeypatch) -> None:
    monkeypatch.setenv("INPUT_VERBOSE", "false")
    monkeypatch.setenv("RUNNER_DEBUG", "1")
    assert ActionInputs.get_verbose() is True


def test_validate_inputs_raises_on_blank_output_path(monkeypatch, caplog) -> None:
    monkeypatch.setenv("INPUT_OUTPUT_PATH", "   ")

    caplog.set_level(logging.ERROR)
    with pytest.raises(ValueError, match="Output path must be a non-empty string\."):
        ActionInputs.validate_inputs()

    assert "Output path must be a non-empty string." in caplog.text
