#
# Copyright 2023 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Unit tests for PDF generator."""

import pytest

from generator.pdf_generator import FileIOError, PdfGenerator, RenderingError


def test_generate_pdf_creates_file(tmp_path):
    """Test that generate_pdf creates a valid PDF file."""
    generator = PdfGenerator()
    output_path = tmp_path / "output.pdf"
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    html = "<html><body><h1>Test Document</h1></body></html>"

    generator.generate_pdf(html, str(output_path), str(template_dir))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generate_pdf_creates_parent_directories(tmp_path):
    """Test that generate_pdf creates parent directories if they don't exist."""
    generator = PdfGenerator()
    output_path = tmp_path / "nested" / "dir" / "output.pdf"
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    html = "<html><body><h1>Test Document</h1></body></html>"

    generator.generate_pdf(html, str(output_path), str(template_dir))

    assert output_path.exists()
    assert output_path.parent.exists()


def test_generate_pdf_raises_rendering_error_on_bad_html(tmp_path, mocker):
    """Test that generate_pdf raises RenderingError on WeasyPrint failure."""
    generator = PdfGenerator()
    output_path = tmp_path / "output.pdf"
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    # Mock weasyprint.HTML to raise an exception
    mock_html_class = mocker.patch("generator.pdf_generator.HTML")
    mock_html_class.side_effect = Exception("WeasyPrint error")

    html = "<html><body><h1>Test</h1></body></html>"

    with pytest.raises(RenderingError, match="Rendering failed"):
        generator.generate_pdf(html, str(output_path), str(template_dir))


def test_generate_pdf_raises_file_io_error_on_write_failure(tmp_path, mocker):
    """Test that generate_pdf raises FileIOError on write failure."""
    generator = PdfGenerator()
    output_path = tmp_path / "output.pdf"
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    # Mock Path.mkdir to raise OSError
    mocker.patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied"))

    html = "<html><body><h1>Test</h1></body></html>"

    with pytest.raises(FileIOError, match="File I/O error"):
        generator.generate_pdf(html, str(output_path), str(template_dir))


def test_generate_pdf_with_valid_html_and_css(tmp_path):
    """Test that generate_pdf works with HTML containing CSS."""
    generator = PdfGenerator()
    output_path = tmp_path / "output.pdf"
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    html = """
    <html>
    <head>
        <style>
            body { font-family: sans-serif; }
            h1 { color: blue; }
        </style>
    </head>
    <body>
        <h1>Test Document</h1>
        <p>This is a test paragraph.</p>
    </body>
    </html>
    """

    generator.generate_pdf(html, str(output_path), str(template_dir))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_error_classes_are_exception_subclasses():
    """Test that custom error classes are proper Exception subclasses."""
    assert issubclass(RenderingError, Exception)
    assert issubclass(FileIOError, Exception)
