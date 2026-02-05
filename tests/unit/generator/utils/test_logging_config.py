import logging

from generator.utils.logging_config import setup_logging


def test_setup_logging_uses_info_by_default(monkeypatch) -> None:
    captured = {}

    def fake_basic_config(**kwargs):
        captured.update(kwargs)

    monkeypatch.delenv("INPUT_VERBOSE", raising=False)
    monkeypatch.delenv("RUNNER_DEBUG", raising=False)

    monkeypatch.setattr(logging, "basicConfig", fake_basic_config)
    monkeypatch.setattr(logging, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(logging, "debug", lambda *args, **kwargs: None)

    setup_logging()
    assert captured["level"] == logging.INFO


def test_setup_logging_uses_debug_when_runner_debug(monkeypatch) -> None:
    captured = {}

    def fake_basic_config(**kwargs):
        captured.update(kwargs)

    monkeypatch.setenv("RUNNER_DEBUG", "1")
    monkeypatch.setenv("INPUT_VERBOSE", "false")

    monkeypatch.setattr(logging, "basicConfig", fake_basic_config)
    monkeypatch.setattr(logging, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(logging, "debug", lambda *args, **kwargs: None)

    setup_logging()
    assert captured["level"] == logging.DEBUG


def test_setup_logging_uses_debug_when_verbose(monkeypatch) -> None:
    """Test that verbose input enables debug logging."""
    captured = {}

    def fake_basic_config(**kwargs):
        captured.update(kwargs)

    monkeypatch.delenv("RUNNER_DEBUG", raising=False)
    monkeypatch.setenv("INPUT_VERBOSE", "true")

    monkeypatch.setattr(logging, "basicConfig", fake_basic_config)
    monkeypatch.setattr(logging, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(logging, "debug", lambda *args, **kwargs: None)

    setup_logging()
    assert captured["level"] == logging.DEBUG
