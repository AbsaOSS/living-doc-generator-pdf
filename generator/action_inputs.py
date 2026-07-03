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

Inputs are read from ``INPUT_*`` environment variables. This is the single
input layer for the action; parsing and validation live here only.
"""

import logging
import os
from typing import Optional

from generator.utils.constants import (
    DEBUG_HTML,
    DOCUMENT_TITLE,
    DOCUMENT_TYPE,
    DOCUMENT_TYPES,
    OUTPUT_PATH,
    PDF_READY_JSON,
    SCHEMA_PATH,
    SOURCE_PATH,
    TEMPLATE_PATH,
    VERBOSE,
)
from generator.utils.gh_action import get_action_input

logger = logging.getLogger(__name__)


def _parse_boolean(value: str | None, default: str = "false") -> bool:
    """Parse a boolean string value.

    Accepts: true, false, 1, 0, yes, no (case-insensitive).

    Args:
        value: The string value to parse (can be None).
        default: Default value if input is empty or None.

    Returns:
        Boolean interpretation of the value.
    """
    normalized = (value or default).strip().lower()
    return normalized in ("true", "1", "yes")


class ActionInputs:
    """Read inputs from the GitHub Actions environment."""

    @staticmethod
    def get_source_path() -> str:
        """Return the path to the source JSON input file (required).

        Reads ``source-path``. Falls back to the deprecated ``pdf-ready-json``
        alias with a warning when ``source-path`` is not provided.

        Returns:
            Path to the source JSON file.

        Raises:
            ValueError: If neither input is provided.
        """
        raw = get_action_input(SOURCE_PATH, "")
        value = (raw or "").strip()
        if value:
            return value

        legacy = (get_action_input(PDF_READY_JSON, "") or "").strip()
        if legacy:
            logger.warning(
                "Input 'pdf_ready_json' is deprecated; use 'source-path' instead. "
                "The alias will be removed in the next major release."
            )
            return legacy

        logger.error("source-path input is required but was not provided.")
        raise ValueError("source-path input is required but was not provided.")

    @staticmethod
    def get_template_path() -> Optional[str]:
        """Return the custom template directory path (optional).

        Returns:
            Path to the template directory, or None if not provided.
        """
        raw = get_action_input(TEMPLATE_PATH, "")
        value = (raw or "").strip()
        return value or None

    @staticmethod
    def get_document_type() -> Optional[str]:
        """Return the built-in document type (optional).

        Returns:
            One of the built-in document types, or None if not provided.
        """
        raw = get_action_input(DOCUMENT_TYPE, "")
        value = (raw or "").strip()
        return value or None

    @staticmethod
    def get_schema_path() -> Optional[str]:
        """Return the JSON Schema path for source validation (optional).

        Returns:
            Path to a JSON Schema file, or None if validation is disabled.
        """
        raw = get_action_input(SCHEMA_PATH, "")
        value = (raw or "").strip()
        return value or None

    @staticmethod
    def get_output_path() -> str:
        """Return the output file path for the generated PDF (default: 'output.pdf')."""
        raw = get_action_input(OUTPUT_PATH, "output.pdf")
        return (raw or "output.pdf").strip()

    @staticmethod
    def get_document_title() -> Optional[str]:
        """Return the document title override (optional).

        Returns:
            The configured title, or None when the caller should derive a default.
        """
        raw = get_action_input(DOCUMENT_TITLE, "")
        value = (raw or "").strip()
        return value or None

    @staticmethod
    def get_debug_html() -> bool:
        """Return True if debug HTML should be saved.

        Accepts: true, false, 1, 0, yes, no (case-insensitive).
        """
        raw = get_action_input(DEBUG_HTML, "false")
        return _parse_boolean(raw)

    @staticmethod
    def get_verbose() -> bool:
        """Return True if verbose/debug logging should be enabled.

        Accepts: true, false, 1, 0, yes, no (case-insensitive).
        Also returns True if RUNNER_DEBUG is set to '1'.
        """
        if os.getenv("RUNNER_DEBUG", "0") == "1":
            return True
        raw = get_action_input(VERBOSE, "false")
        return _parse_boolean(raw)

    @staticmethod
    def validate_inputs() -> None:
        """Validate inputs and raise ValueError on invalid configuration.

        Raises:
            ValueError: When required inputs are missing or invalid.
        """
        output_path = ActionInputs.get_output_path()
        if not output_path:
            logger.error("Output path must be a non-empty string.")
            raise ValueError("Output path must be a non-empty string.")

        # source-path is required (also covers the deprecated alias).
        ActionInputs.get_source_path()

        template_path = ActionInputs.get_template_path()
        document_type = ActionInputs.get_document_type()

        if not template_path and not document_type:
            logger.error("Either template-path or document-type must be provided.")
            raise ValueError("Either template-path or document-type must be provided.")

        if document_type and document_type not in DOCUMENT_TYPES:
            allowed = " | ".join(DOCUMENT_TYPES)
            logger.error("Invalid document-type '%s'. Allowed values: %s", document_type, allowed)
            raise ValueError(f"Invalid document-type '{document_type}'. Allowed values: {allowed}")
