import logging

from requests.exceptions import RequestException, Timeout

from generator.utils.decorators import safe_call_decorator


def test_safe_call_decorator_returns_value_on_success(noop_rate_limiter) -> None:
    @safe_call_decorator(noop_rate_limiter)
    def ok() -> int:
        return 123

    assert ok() == 123


def test_safe_call_decorator_returns_none_on_timeout(noop_rate_limiter, caplog) -> None:
    @safe_call_decorator(noop_rate_limiter)
    def boom() -> None:
        raise Timeout("t")

    caplog.set_level(logging.ERROR)
    assert boom() is None
    assert "Network error calling" in caplog.text


def test_safe_call_decorator_returns_none_on_request_exception(noop_rate_limiter, caplog) -> None:
    @safe_call_decorator(noop_rate_limiter)
    def boom() -> None:
        raise RequestException("r")

    caplog.set_level(logging.ERROR)
    assert boom() is None
    assert "HTTP error calling" in caplog.text


def test_safe_call_decorator_returns_none_on_unexpected_exception(noop_rate_limiter, caplog) -> None:
    @safe_call_decorator(noop_rate_limiter)
    def boom() -> None:
        raise RuntimeError("x")

    caplog.set_level(logging.ERROR)
    assert boom() is None
    assert "Unexpected error calling" in caplog.text
