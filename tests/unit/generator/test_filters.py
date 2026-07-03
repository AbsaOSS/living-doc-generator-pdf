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

from generator.filters import (
    default_if_none_filter,
    format_datetime_filter,
    markdown_filter,
    natural_sort_filter,
)


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
    assert 'href="https://github.com"' in link_result
    assert ">GitHub</a>" in link_result


def test_markdown_filter_strips_script_tag() -> None:
    """markdown_filter must sanitize <script> tags from the output."""
    result = markdown_filter("<script>alert('xss')</script>")
    assert "<script>" not in result
    assert "alert" not in result


def test_markdown_filter_strips_inline_event_handler() -> None:
    """markdown_filter must strip inline event handlers from HTML output."""
    result = markdown_filter('[click me](http://example.com " onmouseover=alert(1))')
    assert "onmouseover" not in result


def test_markdown_filter_strips_raw_html_in_input() -> None:
    """Raw HTML injected via source JSON must not pass through unsanitized."""
    result = markdown_filter('<img src=x onerror=alert(1)>')
    assert "onerror" not in result


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


def test_default_if_none_returns_value_when_present() -> None:
    """default_if_none returns the value when it is not None."""
    assert default_if_none_filter("hello") == "hello"
    assert default_if_none_filter(0) == 0


def test_default_if_none_returns_fallback_when_none() -> None:
    """default_if_none returns the fallback when the value is None."""
    assert default_if_none_filter(None) == ""
    assert default_if_none_filter(None, "N/A") == "N/A"


def test_natural_sort_orders_embedded_numbers() -> None:
    """natural_sort orders IDs by embedded number, not lexicographically."""
    assert natural_sort_filter(["US-10", "US-2", "US-1"]) == ["US-1", "US-2", "US-10"]


def test_natural_sort_by_attribute() -> None:
    """natural_sort sorts dicts by a named attribute."""
    items = [{"id": "US-10"}, {"id": "US-2"}, {"id": "US-1"}]
    result = natural_sort_filter(items, attribute="id")
    assert [i["id"] for i in result] == ["US-1", "US-2", "US-10"]


def test_natural_sort_handles_empty_and_none() -> None:
    """natural_sort returns an empty list for falsy input and tolerates None values."""
    assert natural_sort_filter(None) == []
    assert natural_sort_filter([]) == []
    items = [{"id": "US-2"}, {"id": None}, {"id": "US-1"}]
    result = natural_sort_filter(items, attribute="id")
    assert [i["id"] for i in result] == [None, "US-1", "US-2"]

