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

"""Jinja2 custom filters for template rendering."""

import logging
import re
from datetime import datetime
from typing import Any, Iterable, Optional

import markdown

logger = logging.getLogger(__name__)

_NATURAL_CHUNK_RE = re.compile(r"(\d+)")


def markdown_filter(text: Optional[str]) -> str:
    """Convert Markdown text to HTML.

    Args:
        text: Markdown string or None

    Returns:
        HTML string, or empty string if input is None/empty
    """
    if not text:
        return ""
    return markdown.markdown(text)


def format_datetime_filter(iso_timestamp: Optional[str], format_str: str = "%Y-%m-%d %H:%M") -> str:
    """Format ISO 8601 timestamp to human-readable format.

    Args:
        iso_timestamp: ISO 8601 timestamp string or None
        format_str: strftime format string

    Returns:
        Formatted date string, or empty string if input is None/empty
    """
    if not iso_timestamp:
        return ""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        return dt.strftime(format_str)
    except (ValueError, AttributeError) as e:
        logger.warning("Failed to parse timestamp '%s': %s", iso_timestamp, e)
        return ""


def default_if_none_filter(value: Any, fallback: Any = "") -> Any:
    """Return ``fallback`` when ``value`` is None, otherwise ``value``.

    Args:
        value: The value to inspect.
        fallback: Value to return when ``value`` is None.

    Returns:
        ``value`` if it is not None, else ``fallback``.
    """
    return fallback if value is None else value


def _natural_key(text: str) -> list[Any]:
    """Build a natural-sort key splitting digit runs into integers."""
    parts = _NATURAL_CHUNK_RE.split(text)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def natural_sort_filter(items: Optional[Iterable[Any]], attribute: Optional[str] = None) -> list[Any]:
    """Sort an iterable using natural (human) ordering of embedded numbers.

    Ensures IDs like ``US-2`` sort before ``US-10`` instead of lexicographically.

    Args:
        items: Iterable of values or dicts/objects to sort.
        attribute: Optional attribute/key name to sort by. When omitted, the
            items themselves are used as the sort key.

    Returns:
        A new list sorted in natural ascending order.
    """
    if not items:
        return []

    materialized = list(items)

    def key(item: Any) -> list[Any]:
        if attribute is None:
            value = item
        elif isinstance(item, dict):
            value = item.get(attribute, "")
        else:
            value = getattr(item, attribute, "")
        return _natural_key("" if value is None else str(value))

    return sorted(materialized, key=key)
