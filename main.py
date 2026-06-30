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

Implements the processing pipeline:
1. Validate inputs
2. Load source JSON (optionally validate against a schema)
3. Resolve the template set (built-in document-type and/or custom template-path)
4. Render HTML using Jinja2 templates with injected ``meta``
5. Save debug HTML (if enabled)
6. Generate the PDF using WeasyPrint
7. Generate pdf_report.json with statistics
"""

import logging
from pathlib import Path

from generator.action_inputs import ActionInputs
from generator.models import build_meta
from generator.pdf_generator import FileIOError, PdfGenerator, RenderingError
from generator.report_generator import generate_pdf_report
from generator.schema_validator import SchemaValidationError, load_source
from generator.template_renderer import TemplateError, TemplateRenderer
from generator.utils.constants import DEFAULT_DOCUMENT_TITLES
from generator.utils.gh_action import set_action_failed, set_action_output
from generator.utils.logging_config import setup_logging


def _resolve_document_title(document_type: str | None, source_path: str) -> str:
    """Resolve the cover-page title.

    Resolution order: explicit document-title input, then the built-in default
    for the document type, then the basename of the source file (no extension).
    """
    title = ActionInputs.get_document_title()
    if title:
        return title
    if document_type and document_type in DEFAULT_DOCUMENT_TITLES:
        return DEFAULT_DOCUMENT_TITLES[document_type]
    return Path(source_path).stem


def run() -> None:
    """Run the Living Doc Generator PDF action."""
    setup_logging()
    logger = logging.getLogger(__name__)
    verbose = ActionInputs.get_verbose()
    logger.info("Starting 'Living Doc Generator PDF' GitHub Action")

    try:
        # Step 1: Validate inputs
        ActionInputs.validate_inputs()

        # Step 2: Load source JSON (optionally validate against a schema)
        source_path = ActionInputs.get_source_path()
        schema_path = ActionInputs.get_schema_path()
        logger.info("Loading source JSON from %s", source_path)
        data = load_source(source_path, schema_path)

        # Step 3: Resolve template set
        template_path = ActionInputs.get_template_path()
        document_type = ActionInputs.get_document_type()
        if template_path:
            template_pack_type = "custom"
            template_pack_path = template_path
        else:
            template_pack_type = "built-in"
            template_pack_path = document_type or "built-in"

        renderer = TemplateRenderer(template_path=template_path, document_type=document_type)

        # Step 4: Render HTML
        document_title = _resolve_document_title(document_type, source_path)
        meta = build_meta(document_title, source_path).to_dict()
        logger.info("Rendering HTML for document '%s'", document_title)
        html = renderer.render(data, meta)

        # Step 5: Save debug HTML (if enabled)
        output_path = ActionInputs.get_output_path()
        debug_html = ActionInputs.get_debug_html()
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
        pdf_generator.generate_pdf(html, output_path, renderer.base_dir)
        set_action_output("pdf-path", str(Path(output_path).absolute()))

        # Step 7: Generate pdf_report.json
        logger.info("Generating PDF report")
        report_path = generate_pdf_report(
            input_file=source_path,
            output_file=output_path,
            template_pack_type=template_pack_type,
            template_pack_path=template_pack_path,
            data=data,
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
        set_action_failed(str(exc), exit_code=1)

    except SchemaValidationError as exc:
        # Exit code 2: Schema validation failure
        logger.error("Schema validation failed: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(str(exc), exit_code=2)

    except TemplateError as exc:
        # Exit code 3: Template error
        logger.error("Template error: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(str(exc), exit_code=3)

    except RenderingError as exc:
        # Exit code 4: Rendering error
        logger.error("Rendering failed: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(str(exc), exit_code=4)

    except FileIOError as exc:
        # Exit code 5: File I/O error
        logger.error("File I/O error: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(str(exc), exit_code=5)

    except Exception as exc:  # pylint: disable=broad-except
        # Exit code 1: Unexpected error
        logger.error("Unexpected error: %s", str(exc))
        if verbose:
            logger.exception("Stack trace:")
        set_action_failed(f"Unexpected error: {str(exc)}", exit_code=1)


if __name__ == "__main__":
    run()
