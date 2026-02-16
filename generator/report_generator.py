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

"""PDF report generation for statistics and diagnostics."""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_pdf_report(
    input_file: str,
    output_file: str,
    template_pack_type: str,
    template_pack_path: str,
    pdf_ready_data: dict,
    pdf_path: str,
    errors: list[dict],
    warnings: list[dict],
) -> str:
    """Generate pdf_report.json with statistics and diagnostics.

    Args:
        input_file: Path to pdf_ready.json
        output_file: Path to generated PDF
        template_pack_type: "built-in" or "custom"
        template_pack_path: Template directory path or "built-in"
        pdf_ready_data: Parsed pdf_ready.json data
        pdf_path: Path to generated PDF file
        errors: List of error dictionaries
        warnings: List of warning dictionaries

    Returns:
        Path to the generated pdf_report.json file
    """
    # Count user stories
    user_stories = pdf_ready_data.get("content", {}).get("user_stories", [])
    user_story_count = len(user_stories)

    # Get PDF file size
    pdf_file = Path(pdf_path)
    file_size_bytes = pdf_file.stat().st_size if pdf_file.exists() else 0

    # Check for missing sections in user stories
    report_warnings = list(warnings)
    for idx, story in enumerate(user_stories):
        story_id = story.get("id", f"story[{idx}]")
        sections = story.get("sections", {})

        if not sections.get("acceptance_criteria"):
            report_warnings.append(
                {
                    "level": "warning",
                    "message": f"User story '{story_id}' has no acceptance_criteria section",
                    "context": f"user_stories[{idx}]",
                }
            )

    # Build report structure
    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input_file": input_file,
        "output_file": output_file,
        "template_pack": {"type": template_pack_type, "path": template_pack_path},
        "statistics": {
            "user_story_count": user_story_count,
            "total_pages": 0,  # WeasyPrint doesn't easily expose page count
            "file_size_bytes": file_size_bytes,
        },
        "errors": errors,
        "warnings": report_warnings,
    }

    # Save report to same directory as PDF
    report_path = pdf_file.parent / "pdf_report.json"
    logger.info("Generating PDF report at %s", report_path)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(
        "Report generated: %d user stories, %d warnings, %d errors",
        user_story_count,
        len(report_warnings),
        len(errors),
    )

    return str(report_path)
