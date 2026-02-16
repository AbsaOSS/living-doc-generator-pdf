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
from datetime import datetime
from typing import Optional

import markdown

logger = logging.getLogger(__name__)


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
