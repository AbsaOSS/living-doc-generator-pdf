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

"""Main entrypoint for the Living Doc Generator PDF GitHub Action.

This module implements the full processing pipeline:
1. Load and validate pdf_ready.json
2. Render HTML using Jinja2 templates
3. Save debug HTML (if enabled)
4. Generate PDF using WeasyPrint
5. Generate pdf_report.json with statistics
"""

import logging
import sys
from pathlib import Path

from generator.action_inputs import ActionInputs
from generator.pdf_generator import FileIOError, PdfGenerator, RenderingError
from generator.report_generator import generate_pdf_report
from generator.schema_validator import SchemaValidationError, validate_pdf_ready_json
from generator.template_renderer import TemplateError, TemplateRenderer
from generator.utils.gh_action import set_action_failed, set_action_output
from generator.utils.logging_config import setup_logging


def run() -> None:
    """Run the Living Doc Generator PDF action.

    Implements the full processing pipeline from SPEC.md § 5.1.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    verbose = ActionInputs.get_verbose()
    logger.info("Starting 'Living Doc Generator PDF' GitHub Action")

    try:
        # Step 1: Validate inputs
        ActionInputs.validate_inputs()

        # Step 2: Load and validate pdf_ready.json
        pdf_ready_json_path = ActionInputs.get_pdf_ready_json()
        logger.info("Loading pdf_ready.json from %s", pdf_ready_json_path)
        pdf_ready_data = validate_pdf_ready_json(pdf_ready_json_path)

        # Step 3: Load template pack
        template_dir = ActionInputs.get_template_dir()
        if template_dir:
            template_pack_type = "custom"
            template_pack_path = template_dir
            logger.info("Using custom template pack from %s", template_dir)
        else:
            template_pack_type = "built-in"
            template_pack_path = "built-in"
            template_dir = str(Path(__file__).parent / "generator" / "templates")
            logger.info("Using built-in template pack")

        renderer = TemplateRenderer(ActionInputs.get_template_dir())

        # Step 4: Render HTML
        logger.info("Rendering HTML from pdf_ready.json")
        html = renderer.render(pdf_ready_data)

        # Step 5: Save debug HTML (if enabled)
        output_path = ActionInputs.get_output_path()
        debug_html = ActionInputs.get_debug_html()
        html_path = None
        if debug_html:
            output_file = Path(output_path)
            html_filename = f"{output_file.stem}_rendered.html"
            html_path = str(output_file.parent / html_filename)
            logger.info("Saving debug HTML to %s", html_path)
            Path(html_path).write_text(html, encoding="utf-8")
            set_action_output("html-path", html_path)

        # Step 6: Generate PDF
        logger.info("Generating PDF from rendered HTML")
        pdf_generator = PdfGenerator()
        pdf_generator.generate_pdf(html, output_path, template_dir)
        set_action_output("pdf-path", str(Path(output_path).absolute()))

        # Step 7: Generate pdf_report.json
        logger.info("Generating PDF report")
        report_path = generate_pdf_report(
            input_file=pdf_ready_json_path,
            output_file=output_path,
            template_pack_type=template_pack_type,
            template_pack_path=template_pack_path,
            pdf_ready_data=pdf_ready_data,
            pdf_path=output_path,
            errors=[],
            warnings=[],
        )
        set_action_output("report-path", report_path)

        logger.info("GitHub Action 'Living Doc Generator PDF' completed successfully")

    except ValueError as exc:
        # Exit code 1: Invalid input
        logger.error("Invalid input: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(str(exc))
        sys.exit(1)

    except SchemaValidationError as exc:
        # Exit code 2: Schema validation failure
        logger.error("Schema validation failed: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(str(exc))
        sys.exit(2)

    except TemplateError as exc:
        # Exit code 3: Template error
        logger.error("Template error: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(str(exc))
        sys.exit(3)

    except RenderingError as exc:
        # Exit code 4: Rendering error
        logger.error("Rendering failed: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(str(exc))
        sys.exit(4)

    except FileIOError as exc:
        # Exit code 5: File I/O error
        logger.error("File I/O error: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(str(exc))
        sys.exit(5)

    except Exception as exc:  # pylint: disable=broad-except
        # Exit code 1: Unexpected error
        logger.error("Unexpected error: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(f"Unexpected error: {str(exc)}")
        sys.exit(1)


if __name__ == "__main__":
    run()
