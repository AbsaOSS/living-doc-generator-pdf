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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _count_items(data: dict[str, Any]) -> int:
    """Count top-level renderable items in a generic source document."""
    for key in ("items", "user_stories"):
        value = data.get(key)
        if isinstance(value, list):
            return len(value)
    return 0


def generate_pdf_report(
    input_file: str,
    output_file: str,
    template_pack_type: str,
    template_pack_path: str,
    data: dict[str, Any],
    pdf_path: str,
    errors: list[dict],
    warnings: list[dict],
) -> str:
    """Generate pdf_report.json with statistics and diagnostics.

    Args:
        input_file: Path to the source JSON file.
        output_file: Path to the generated PDF.
        template_pack_type: "built-in" or "custom".
        template_pack_path: Template directory path or "built-in".
        data: Parsed source JSON data.
        pdf_path: Path to the generated PDF file.
        errors: List of error dictionaries.
        warnings: List of warning dictionaries.

    Returns:
        Path to the generated pdf_report.json file.
    """
    item_count = _count_items(data)

    pdf_file = Path(pdf_path)
    file_size_bytes = pdf_file.stat().st_size if pdf_file.exists() else 0

    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input_file": input_file,
        "output_file": output_file,
        "template_pack": {"type": template_pack_type, "path": template_pack_path},
        "statistics": {
            "item_count": item_count,
            "total_pages": 0,  # WeasyPrint doesn't easily expose page count
            "file_size_bytes": file_size_bytes,
        },
        "errors": errors,
        "warnings": list(warnings),
    }

    report_path = pdf_file.parent / "pdf_report.json"
    logger.info("Generating PDF report at %s", report_path)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(
        "Report generated: %d items, %d warnings, %d errors",
        item_count,
        len(warnings),
        len(errors),
    )

    return str(report_path)
