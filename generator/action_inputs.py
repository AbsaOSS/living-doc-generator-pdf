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
    SOURCE_PATH,
    TEMPLATE_DIR,
    TEMPLATE_PATH,
    VERBOSE,
)
from generator.utils.gh_action import get_action_input

logger = logging.getLogger(__name__)


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
        normalized = (raw or "false").strip().lower()
        return normalized in ("true", "1", "yes")

    @staticmethod
    def get_verbose() -> bool:
        """Return True if verbose/debug logging should be enabled.

        Accepts: true, false, 1, 0, yes, no (case-insensitive)
        Also returns True if RUNNER_DEBUG is set to '1'
        """
        raw = get_action_input(VERBOSE, "false")
        normalized = (raw or "false").strip().lower()
        return os.getenv("RUNNER_DEBUG", "0") == "1" or normalized in ("true", "1", "yes")

    # Legacy methods (deprecated - to be removed in v2.0)

    @staticmethod
    def get_document_title() -> str:
        """Return the document title to embed in the generated PDF (deprecated)."""
        raw = get_action_input(DOCUMENT_TITLE, "Living Documentation")
        return (raw or "Living Documentation").strip()

    @staticmethod
    def get_source_path() -> str:
        """Return the source directory path containing documentation inputs (deprecated)."""
        raw = get_action_input(SOURCE_PATH, "docs")
        return (raw or "docs").strip()

    @staticmethod
    def get_template_path() -> Optional[str]:
        """Return an optional template path used for PDF rendering (deprecated)."""
        raw = get_action_input(TEMPLATE_PATH, "")
        value = (raw or "").strip()
        return value or None

    @staticmethod
    def validate_inputs() -> None:
        """Validate required inputs and raise ValueError on invalid configuration."""
        output_path = ActionInputs.get_output_path()
        if not output_path:
            logger.error("Output path must be a non-empty string.")
            raise ValueError("Output path must be a non-empty string.")

        # Validate pdf_ready_json if using new contract
        try:
            pdf_ready_json = ActionInputs.get_pdf_ready_json()
            if pdf_ready_json and not pdf_ready_json.strip():
                logger.error("pdf_ready_json must be a non-empty string.")
                raise ValueError("pdf_ready_json must be a non-empty string.")
        except ValueError:
            # pdf_ready_json is optional during transition period
            pass
