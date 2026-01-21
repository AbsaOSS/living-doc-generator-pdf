import main


def test_run_outputs_pdf_path_on_success(monkeypatch, tmp_path) -> None:
    output_calls: list[tuple[str, str]] = []
    failed_calls: list[str] = []

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))

    class FakeGenerator:
        def generate(self):
            return str(tmp_path / "out.pdf")

    monkeypatch.setattr(main, "PdfGenerator", FakeGenerator)
    monkeypatch.setattr(main, "set_action_output", lambda name, value: output_calls.append((name, value)))
    monkeypatch.setattr(main, "set_action_failed", lambda msg: failed_calls.append(msg))

    main.run()

    assert failed_calls == []
    assert output_calls == [("pdf-path", str(tmp_path / "out.pdf"))]


def test_run_fails_when_generator_returns_none(monkeypatch) -> None:
    failed_calls: list[str] = []

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))

    class FakeGenerator:
        def generate(self):
            return None

    monkeypatch.setattr(main, "PdfGenerator", FakeGenerator)
    monkeypatch.setattr(main, "set_action_output", lambda name, value: None)
    monkeypatch.setattr(main, "set_action_failed", lambda msg: failed_calls.append(msg))

    main.run()

    assert failed_calls == ["Failed to generate PDF. See logs for details."]


def test_run_fails_when_generator_raises(monkeypatch) -> None:
    failed_calls: list[str] = []

    monkeypatch.setattr(main, "setup_logging", lambda: None)
    monkeypatch.setattr(main.ActionInputs, "validate_inputs", staticmethod(lambda: None))

    class FakeGenerator:
        def generate(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(main, "PdfGenerator", FakeGenerator)
    monkeypatch.setattr(main, "set_action_output", lambda name, value: None)
    monkeypatch.setattr(main, "set_action_failed", lambda msg: failed_calls.append(msg))

    main.run()

    assert len(failed_calls) == 1
    assert failed_calls[0].startswith("Failed to generate PDF. Error: ")
