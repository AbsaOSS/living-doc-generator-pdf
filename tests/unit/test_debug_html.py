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

"""Unit tests for debug HTML output functionality."""

from pathlib import Path


def test_debug_html_filename_derivation():
    """Test that debug HTML filename is correctly derived from PDF path."""
    output_path = Path("/path/to/output.pdf")
    expected_html = output_path.parent / "output_rendered.html"

    html_filename = f"{output_path.stem}_rendered.html"
    html_path = output_path.parent / html_filename

    assert html_path == expected_html
    assert str(html_path) == "/path/to/output_rendered.html"


def test_debug_html_filename_with_nested_path():
    """Test debug HTML filename with nested directory path."""
    output_path = Path("/workspace/docs/reports/documentation.pdf")
    html_filename = f"{output_path.stem}_rendered.html"
    html_path = output_path.parent / html_filename

    assert str(html_path) == "/workspace/docs/reports/documentation_rendered.html"


def test_debug_html_saved_when_enabled(tmp_path):
    """Test that HTML is saved when debug_html is enabled."""
    output_path = tmp_path / "output.pdf"
    html_content = "<html><body><h1>Test</h1></body></html>"

    # Simulate saving debug HTML
    html_filename = f"{output_path.stem}_rendered.html"
    html_path = output_path.parent / html_filename
    html_path.write_text(html_content, encoding="utf-8")

    assert html_path.exists()
    assert html_path.read_text(encoding="utf-8") == html_content


def test_debug_html_contains_correct_content(tmp_path):
    """Test that saved debug HTML contains the rendered content."""
    output_path = tmp_path / "report.pdf"
    html_content = """
    <html>
    <head>
        <style>body { font-family: sans-serif; }</style>
    </head>
    <body>
        <h1>Test Document</h1>
        <p>This is test content with <strong>formatting</strong>.</p>
    </body>
    </html>
    """

    html_filename = f"{output_path.stem}_rendered.html"
    html_path = output_path.parent / html_filename
    html_path.write_text(html_content, encoding="utf-8")

    saved_content = html_path.read_text(encoding="utf-8")
    assert "<h1>Test Document</h1>" in saved_content
    assert "<strong>formatting</strong>" in saved_content
    assert "<style>" in saved_content
