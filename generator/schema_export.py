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

"""
Schema export for Pydantic models.

Exports Pydantic models to JSON Schema format as an independent artifact.

Schemas are saved to the `schemas/` directory next to src/ directory,
making them available for distribution and use by downstream consumers.

See SCHEMA_SYNC.md for details.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from generator.models import PdfReadyJson

logger = logging.getLogger(__name__)


def get_schema_version() -> str:
    """
    Get the version of the PDF-ready input contract schema.

    This is independent of the package version and represents
    the version of the pdf_ready.json input schema.

    Returns:
        Version string (semver format)
    """
    return "1.0"


def get_default_schema_path() -> Path:
    """
    Get the default schema export directory path.

    Returns:
        Path to schemas/ directory (generator/schemas/)
    """
    # Navigate from generator/ to generator/schemas/
    package_root = Path(__file__).parent
    schemas_dir = package_root / "schemas"
    return schemas_dir


def export_schema(output_path: Optional[str | Path] = None) -> dict:
    """
    Export the PdfReadyJson model schema to JSON Schema format.

    This schema represents the authoritative input contract for the data format.

    Args:
        output_path: Optional file path to write schema to. If None, uses default
                     location with version: generator/schemas/pdf_ready_v1.0-schema.json

    Returns:
        Dictionary containing the JSON Schema.

    Example:
        >>> schema = export_schema()
        >>> print(schema['properties']['meta'])

        >>> export_schema('custom-location.json')
    """
    schema = PdfReadyJson.model_json_schema()

    # Pin schema version independently of package version
    schema["$schema_version"] = get_schema_version()

    # Use default location if not provided
    if output_path is None:
        schemas_dir = get_default_schema_path()
        schema_version = get_schema_version()
        output_path = schemas_dir / f"pdf_ready_v{schema_version}-schema.json"

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    logger.info("Schema exported to: %s", output_file)
    print(f"Schema exported to: {output_file}")

    return schema


if __name__ == "__main__":
    import sys

    # CLI usage:
    #   python -m generator.schema_export  # Uses default location with version
    #   python -m generator.schema_export output.json  # Custom location
    output = sys.argv[1] if len(sys.argv) > 1 else None
    export_schema(output)
    if output is None:
        schema_version = get_schema_version()
        print(f"Default location: {get_default_schema_path() / f'pdf_ready_v{schema_version}-schema.json'}")
