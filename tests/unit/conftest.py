from __future__ import annotations

from collections.abc import Generator

import os
import pathlib

import pytest


@pytest.fixture(autouse=True)
def _clean_action_input_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep unit tests isolated from developer environment variables."""
    for key in list(os.environ.keys()):
        if key.startswith("INPUT_"):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture
def noop_rate_limiter() -> callable:
    """A decorator that applies no rate limiting (test helper)."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


@pytest.fixture
def github_output_file(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Provide a temp file for GITHUB_OUTPUT and set env accordingly."""
    out = tmp_path / "github_output.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    return out
