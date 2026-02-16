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

"""PDF generation using WeasyPrint."""

import logging
from pathlib import Path

from weasyprint import HTML  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class RenderingError(Exception):
    """Exception raised for rendering errors (exit code 4)."""


class FileIOError(Exception):
    """Exception raised for file I/O errors (exit code 5)."""


class PdfGenerator:
    """Generate PDF from rendered HTML using WeasyPrint."""

    def generate_pdf(self, html: str, output_path: str, template_dir: str) -> None:
        """Generate PDF from rendered HTML using WeasyPrint.

        Args:
            html: Rendered HTML string from TemplateRenderer
            output_path: Path to write the PDF file
            template_dir: Path to template directory for asset resolution (base_url)

        Raises:
            RenderingError: When WeasyPrint fails (exit code 4)
            FileIOError: When file writing fails (exit code 5)
        """
        try:
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            logger.info("Writing PDF to %s", output_path)

            # Set base_url to template directory for asset resolution
            base_url = Path(template_dir).absolute().as_uri()
            logger.debug("Using base_url: %s", base_url)

            # Generate PDF using WeasyPrint
            html_doc = HTML(string=html, base_url=base_url)
            html_doc.write_pdf(output_path)

            logger.info("PDF generated successfully (%d bytes)", output_file.stat().st_size)

        except OSError as e:
            msg = f"File I/O error: Failed to write PDF to '{output_path}'. Check file permissions and disk space."
            logger.error(msg)
            raise FileIOError(msg) from e
        except Exception as e:
            msg = f"Rendering failed: WeasyPrint error - {str(e)}. Check HTML/CSS syntax and asset paths."
            logger.error(msg)
            raise RenderingError(msg) from e
