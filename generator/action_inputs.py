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

"""Action input helpers for the Living Doc Generator PDF GitHub Action.

This is a simplified, temporary input surface intended to decouple the repository
from the previous generator contracts.
"""

import logging
import os
from typing import Optional

from generator.utils.constants import (
    DEBUG_HTML,
    DOCUMENT_TITLE,
    OUTPUT_PATH,
    PDF_READY_JSON,
    TEMPLATE_DIR,
    VERBOSE,
)
from generator.utils.gh_action import get_action_input

logger = logging.getLogger(__name__)


def _parse_boolean(value: str | None, default: str = "false") -> bool:
    """Parse a boolean string value.

    Accepts: true, false, 1, 0, yes, no (case-insensitive)

    Args:
        value: The string value to parse (can be None)
        default: Default value if input is empty or None

    Returns:
        Boolean interpretation of the value
    """
    normalized = (value or default).strip().lower()
    return normalized in ("true", "1", "yes")


class ActionInputs:
    """Read inputs from the GitHub Actions environment."""

    @staticmethod
    def get_pdf_ready_json() -> str:
        """Return path to pdf_ready.json file (required).

        Returns:
            Path to pdf_ready.json file

        Raises:
            ValueError: If the input is missing or empty
        """
        raw = get_action_input(PDF_READY_JSON, "")
        value = (raw or "").strip()
        if not value:
            logger.error("pdf_ready_json input is required but was not provided.")
            raise ValueError("pdf_ready_json input is required but was not provided.")
        return value

    @staticmethod
    def get_output_path() -> str:
        """Return the output file path for the generated PDF (default: 'output.pdf')."""
        raw = get_action_input(OUTPUT_PATH, "output.pdf")
        return (raw or "output.pdf").strip()

    @staticmethod
    def get_document_title() -> str:
        """Return the document title (optional, default: 'Document').

        Returns:
            Document title string
        """
        raw = get_action_input(DOCUMENT_TITLE, "Document")
        return (raw or "Document").strip()

    @staticmethod
    def get_template_dir() -> Optional[str]:
        """Return custom template directory path (optional).

        Returns:
            Path to template directory or None if not provided
        """
        raw = get_action_input(TEMPLATE_DIR, "")
        value = (raw or "").strip()
        return value or None

    @staticmethod
    def get_debug_html() -> bool:
        """Return True if debug HTML should be saved.

        Accepts: true, false, 1, 0, yes, no (case-insensitive)
        """
        raw = get_action_input(DEBUG_HTML, "false")
        return _parse_boolean(raw)

    @staticmethod
    def get_verbose() -> bool:
        """Return True if verbose/debug logging should be enabled.

        Accepts: true, false, 1, 0, yes, no (case-insensitive)
        Also returns True if RUNNER_DEBUG is set to '1'
        """
        if os.getenv("RUNNER_DEBUG", "0") == "1":
            return True
        raw = get_action_input(VERBOSE, "false")
        return _parse_boolean(raw)

    @staticmethod
    def validate_inputs() -> None:
        """Validate required inputs and raise ValueError on invalid configuration."""
        output_path = ActionInputs.get_output_path()
        if not output_path:
            logger.error("Output path must be a non-empty string.")
            raise ValueError("Output path must be a non-empty string.")

        # Validate pdf_ready_json if using new contract
        try:
            ActionInputs.get_pdf_ready_json()
        except ValueError:
            # pdf_ready_json is optional during transition period
            pass
