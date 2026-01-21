import pytest

from generator.utils.gh_action import get_action_input, set_action_failed, set_action_output


def test_get_action_input_reads_expected_env_var(monkeypatch) -> None:
    monkeypatch.setenv("INPUT_FOO_BAR", "value")
    assert get_action_input("foo-bar") == "value"


def test_get_action_input_returns_default_when_missing(monkeypatch) -> None:
    monkeypatch.delenv("INPUT_MISSING", raising=False)
    assert get_action_input("missing", default="fallback") == "fallback"


def test_set_action_output_writes_github_output_file(github_output_file) -> None:
    set_action_output("pdf-path", "out.pdf")

    content = github_output_file.read_text(encoding="utf-8")
    assert content == "pdf-path<<EOF\nout.pdfEOF\n"


def test_set_action_failed_writes_error_and_exits(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        set_action_failed("boom")

    assert exc.value.code == 1

    captured = capsys.readouterr()
    assert "::error::boom" in captured.err
