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

from generator.filters import format_datetime_filter, markdown_filter

logger = logging.getLogger(__name__)


class TemplateError(Exception):
    """Exception raised for template errors (exit code 3)."""


class TemplateRenderer:
    """Jinja2-based template renderer with custom and built-in template support."""

    def __init__(self, template_dir: Optional[str] = None) -> None:
        """Initialize renderer with built-in or custom templates.

        Args:
            template_dir: Optional path to custom template directory.
                         If provided, templates override built-in defaults.
                         Missing templates fall back to built-in.
        """
        # Get the built-in templates directory
        built_in_dir = Path(__file__).parent / "templates"

        # Set up loaders
        loaders = []
        if template_dir:
            custom_path = Path(template_dir)
            if not custom_path.exists():
                logger.warning("Custom template directory '%s' does not exist. Using built-in templates.", template_dir)
            else:
                loaders.append(FileSystemLoader(str(custom_path)))
                logger.info("Using custom templates from '%s' with built-in fallback", template_dir)

        loaders.append(FileSystemLoader(str(built_in_dir)))

        # Create Jinja2 environment
        self._env = Environment(
            loader=ChoiceLoader(loaders),
            autoescape=True,
        )

        # Register custom filters
        self._env.filters["markdown"] = markdown_filter
        self._env.filters["format_datetime"] = format_datetime_filter

        logger.debug("TemplateRenderer initialized with %d loader(s)", len(loaders))

    def render(self, pdf_ready_data: dict[str, Any]) -> str:
        """Render HTML from pdf_ready.json data.

        Args:
            pdf_ready_data: Validated dictionary from pdf_ready.json

        Returns:
            Rendered HTML string

        Raises:
            TemplateError: If template not found or syntax error
        """
        try:
            template = self._env.get_template("main.html.jinja")
            html = template.render(**pdf_ready_data)
            logger.info("Template rendered successfully (%d characters)", len(html))
            return html
        except TemplateNotFound as e:
            msg = f"Template error: Template '{e.name}' not found. Check template_dir path or use default templates."
            logger.error(msg)
            raise TemplateError(msg) from e
        except TemplateSyntaxError as e:
            msg = f"Template error: Syntax error in '{e.name}' at line {e.lineno}. Fix template syntax."
            logger.error(msg)
            raise TemplateError(msg) from e
