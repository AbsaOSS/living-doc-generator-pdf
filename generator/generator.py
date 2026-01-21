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

"""PDF generator implementation.

Temporary migration note:
- This currently generates a minimal, valid PDF file without external dependencies.
- It is intended as a placeholder until the real living-doc compilation pipeline is implemented.
"""

import logging
from pathlib import Path
from typing import Optional

from generator.action_inputs import ActionInputs

logger = logging.getLogger(__name__)


def _escape_pdf_string(value: str) -> str:
    """Escape a string for use inside a PDF literal string."""
    value = value.replace("\\", "\\\\")
    value = value.replace("(", "\\(")
    value = value.replace(")", "\\)")
    return value.replace("\r", " ").replace("\n", " ")


def _build_minimal_pdf(text: str) -> bytes:
    """Build a minimal, valid PDF rendering a single line of text."""
    escaped_text = _escape_pdf_string(text)
    content_stream = ("BT\n" "/F1 24 Tf\n" "72 720 Td\n" f"({escaped_text}) Tj\n" "ET\n").encode("utf-8")

    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"

    objects: list[bytes] = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objects.append(
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\n"
        b"endobj\n"
    )
    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    objects.append(
        b"5 0 obj\n"
        + (f"<< /Length {len(content_stream)} >>\n").encode("ascii")
        + b"stream\n"
        + content_stream
        + b"endstream\nendobj\n"
    )

    offsets: list[int] = []
    body = bytearray()
    for obj in objects:
        offsets.append(len(header) + len(body))
        body.extend(obj)

    xref_start = len(header) + len(body)
    xref = bytearray()
    xref.extend(b"xref\n")
    xref.extend(b"0 6\n")
    xref.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        xref.extend((f"{offset:010d} 00000 n \n").encode("ascii"))

    trailer = ("trailer\n" "<< /Size 6 /Root 1 0 R >>\n" "startxref\n" f"{xref_start}\n" "%%EOF\n").encode("ascii")

    return bytes(header + body + xref + trailer)


class PdfGenerator:
    """Generate a PDF from the configured action inputs.

    This placeholder implementation writes a minimal, valid PDF file containing
    the configured document title.
    """

    def generate(self) -> Optional[str]:
        """Generate a PDF and return its path (or None on failure)."""
        output_path = Path(ActionInputs.get_output_path())
        title = ActionInputs.get_document_title()

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            pdf_bytes = _build_minimal_pdf(title)
            logger.info("Writing PDF to %s", output_path)
            output_path.write_bytes(pdf_bytes)
        except OSError:
            logger.exception("Failed writing PDF to %s", output_path)
            return None

        return str(output_path)
