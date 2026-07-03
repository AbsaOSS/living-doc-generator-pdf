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

"""Document metadata injected into every template render.

The action passes raw JSON to templates as ``data`` and injects ``meta`` with
the fields below. There is no Python-side transformation of ``data``.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Meta:
    """Action-injected metadata exposed to templates as ``meta``."""

    document_title: str
    generated_at: str
    source_file: str

    def to_dict(self) -> dict[str, Any]:
        """Return the metadata as a plain dict for template context."""
        return {
            "document_title": self.document_title,
            "generated_at": self.generated_at,
            "source_file": self.source_file,
        }


def build_meta(document_title: str, source_path: str) -> Meta:
    """Build the injected metadata for a render.

    Args:
        document_title: Resolved title shown on the cover page.
        source_path: Path to the source JSON file (basename is exposed).

    Returns:
        A populated :class:`Meta` instance.
    """
    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return Meta(
        document_title=document_title,
        generated_at=generated_at,
        source_file=Path(source_path).name,
    )
