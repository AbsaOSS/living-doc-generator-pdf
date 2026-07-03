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

"""Jinja2-based template renderer with custom and built-in template support."""

import logging
from pathlib import Path
from typing import Any, Optional

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError

from generator.filters import (
    default_if_none_filter,
    format_datetime_filter,
    markdown_filter,
    natural_sort_filter,
)
from generator.utils.constants import DOCUMENT_TYPE_TEMPLATE_DIR

logger = logging.getLogger(__name__)


class TemplateError(Exception):
    """Exception raised for template errors (exit code 3)."""


class TemplateRenderer:
    """Render HTML from generic JSON data using built-in or custom Jinja2 templates."""

    def __init__(self, template_path: Optional[str] = None, document_type: Optional[str] = None) -> None:
        """Initialize the renderer and resolve the template loader chain.

        Resolution rules (see spec §5.2):
            - both template_path and document_type: user files first, built-in
              type set as fallback (partial override).
            - only template_path: the custom directory must be self-contained.
            - only document_type: the built-in set for that type.
            - neither: a TemplateError is raised.

        Args:
            template_path: Optional path to a custom template directory.
            document_type: Optional built-in document type identifier.

        Raises:
            TemplateError: When neither input is provided or the resolved
                directories do not exist.
        """
        loaders: list[FileSystemLoader] = []
        base_dir: Optional[Path] = None

        if template_path:
            custom_path = Path(template_path)
            if not custom_path.exists():
                msg = f"Template error: Template directory '{template_path}' not found. Check template-path."
                logger.error(msg)
                raise TemplateError(msg)
            loaders.append(FileSystemLoader(str(custom_path)))
            base_dir = custom_path
            logger.info("Using custom templates from '%s'", template_path)

        if document_type:
            template_dir_name = DOCUMENT_TYPE_TEMPLATE_DIR.get(document_type, document_type)
            built_in_dir = Path(__file__).parent / "templates" / template_dir_name
            if not built_in_dir.exists():
                msg = f"Template error: Built-in template set '{document_type}' not found."
                logger.error(msg)
                raise TemplateError(msg)
            loaders.append(FileSystemLoader(str(built_in_dir)))
            # Always resolve assets against built-in dir for relative asset paths to work correctly
            # This allows custom templates to partially override while inheriting assets
            if base_dir is None:
                base_dir = built_in_dir
            else:
                # When both custom and built-in are present, assets resolve via the built-in dir
                base_dir = built_in_dir
            logger.info("Using built-in template set '%s'", document_type)

        if not loaders or base_dir is None:
            msg = "Template error: Either template-path or document-type must be provided."
            logger.error(msg)
            raise TemplateError(msg)

        self._base_dir = base_dir
        self._env = Environment(
            loader=ChoiceLoader(loaders),
            autoescape=True,
        )
        self._env.filters["markdown"] = markdown_filter
        self._env.filters["format_datetime"] = format_datetime_filter
        self._env.filters["default_if_none"] = default_if_none_filter
        self._env.filters["natural_sort"] = natural_sort_filter

        logger.debug("TemplateRenderer initialized with %d loader(s)", len(loaders))

    @property
    def base_dir(self) -> str:
        """Return the primary template directory used for asset resolution."""
        return str(self._base_dir)

    def render(self, data: dict[str, Any], meta: dict[str, Any]) -> str:
        """Render the document HTML from raw JSON data and injected metadata.

        Args:
            data: The full parsed JSON source as a plain dict (no transformation).
            meta: Action-injected metadata (document_title, generated_at, source_file).

        Returns:
            Rendered HTML string.

        Raises:
            TemplateError: If a template is missing or has a syntax error.
        """
        try:
            template = self._env.get_template("main.html.jinja")
            html = template.render(data=data, meta=meta)
            logger.info("Template rendered successfully (%d characters)", len(html))
            return html
        except TemplateNotFound as e:
            msg = f"Template error: Template '{e.name}' not found. Check template-path or document-type."
            logger.error(msg)
            raise TemplateError(msg) from e
        except TemplateSyntaxError as e:
            msg = f"Template error: Syntax error in '{e.name}' at line {e.lineno}. Fix template syntax."
            logger.error(msg)
            raise TemplateError(msg) from e
