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

"""Unit tests for custom Jinja2 filters."""

from generator.filters import format_datetime_filter, markdown_filter


def test_markdown_filter_basic() -> None:
    """Test basic Markdown conversion."""
    result = markdown_filter("Hello **world**")
    assert "<strong>world</strong>" in result
    assert "<p>" in result


def test_markdown_filter_headers() -> None:
    """Test H1-H6 headers conversion."""
    text = "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6"
    result = markdown_filter(text)
    assert "<h1>H1</h1>" in result
    assert "<h2>H2</h2>" in result
    assert "<h3>H3</h3>" in result
    assert "<h4>H4</h4>" in result
    assert "<h5>H5</h5>" in result
    assert "<h6>H6</h6>" in result


def test_markdown_filter_lists() -> None:
    """Test ordered and unordered lists."""
    # Unordered list
    ul_text = "- Item 1\n- Item 2\n- Item 3"
    ul_result = markdown_filter(ul_text)
    assert "<ul>" in ul_result
    assert "<li>Item 1</li>" in ul_result

    # Ordered list
    ol_text = "1. First\n2. Second\n3. Third"
    ol_result = markdown_filter(ol_text)
    assert "<ol>" in ol_result
    assert "<li>First</li>" in ol_result


def test_markdown_filter_code() -> None:
    """Test code blocks and inline code."""
    # Inline code
    inline = "Use `print()` to output"
    inline_result = markdown_filter(inline)
    assert "<code>" in inline_result
    assert "print()" in inline_result

    # Code block
    block = "```python\nprint('hello')\n```"
    block_result = markdown_filter(block)
    assert "<code>" in block_result
    assert "print('hello')" in block_result


def test_markdown_filter_links() -> None:
    """Test links and images."""
    # Link
    link = "[GitHub](https://github.com)"
    link_result = markdown_filter(link)
    assert '<a href="https://github.com">GitHub</a>' in link_result


def test_markdown_filter_none() -> None:
    """Test None handling returns empty string."""
    result = markdown_filter(None)
    assert result == ""


def test_markdown_filter_empty() -> None:
    """Test empty string returns empty string."""
    result = markdown_filter("")
    assert result == ""


def test_markdown_filter_whitespace_only() -> None:
    """Test whitespace-only string returns empty string."""
    result = markdown_filter("   ")
    assert result == ""


def test_format_datetime_filter_basic() -> None:
    """Test basic timestamp formatting."""
    result = format_datetime_filter("2026-01-21T12:00:00Z")
    assert "2026-01-21" in result
    assert "12:00" in result


def test_format_datetime_filter_none() -> None:
    """Test None handling returns empty string."""
    result = format_datetime_filter(None)
    assert result == ""


def test_format_datetime_filter_empty() -> None:
    """Test empty string returns empty string."""
    result = format_datetime_filter("")
    assert result == ""


def test_format_datetime_filter_custom_format() -> None:
    """Test custom format strings."""
    result = format_datetime_filter("2026-01-21T12:30:45Z", "%B %d, %Y")
    assert "January 21, 2026" in result


def test_format_datetime_filter_invalid_timestamp() -> None:
    """Test invalid timestamp returns empty string."""
    result = format_datetime_filter("not-a-timestamp")
    assert result == ""


def test_format_datetime_filter_with_timezone() -> None:
    """Test timestamp with timezone offset."""
    result = format_datetime_filter("2026-01-21T12:00:00+02:00")
    assert "2026-01-21" in result
