from pathlib import Path

import pytest

from generator.generator import PdfGenerator


def test_generator_writes_minimal_pdf(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "out.pdf"

    monkeypatch.setenv("INPUT_OUTPUT_PATH", str(output_path))
    monkeypatch.setenv("INPUT_DOCUMENT_TITLE", "Unit Test Title")

    pdf_path = PdfGenerator().generate()

    assert pdf_path == str(output_path)
    assert output_path.exists()

    content = output_path.read_bytes()
    assert content.startswith(b"%PDF-")
    assert b"%%EOF" in content


def test_generator_returns_none_on_write_error(tmp_path: Path, monkeypatch, mocker) -> None:
    """Test that OSError during write returns None."""
    monkeypatch.setenv("INPUT_OUTPUT_PATH", str(tmp_path / "out.pdf"))
    monkeypatch.setenv("INPUT_DOCUMENT_TITLE", "Test")

    mocker.patch.object(Path, "write_bytes", side_effect=OSError("disk full"))
    result = PdfGenerator().generate()

    assert result is None

    assert result is None
