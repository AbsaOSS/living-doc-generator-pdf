#!/usr/bin/env python3
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

"""Verify that the JSON schema file exists and is valid."""

import json
import sys
from pathlib import Path


def main() -> int:
    """Verify schema file exists and is valid JSON."""
    # Locate schema file
    repo_root = Path(__file__).parent.parent
    schema_path = repo_root / "generator" / "schemas" / "pdf_ready_v1.0.json"

    # Check if file exists
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return 1

    print(f"✅ Schema file exists: {schema_path}")

    # Verify it's valid JSON
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        print("✅ Schema file contains valid JSON")
    except json.JSONDecodeError as e:
        print(f"❌ Schema file contains invalid JSON: {e}")
        return 1

    # Verify it follows JSON Schema specification
    required_keys = ["$schema", "type", "properties"]
    for key in required_keys:
        if key not in schema:
            print(f"❌ Schema missing required key: {key}")
            return 1

    print(f"✅ Schema has required keys: {required_keys}")

    # Verify top-level properties exist
    expected_properties = ["schema_version", "meta", "content"]
    actual_properties = list(schema.get("properties", {}).keys())

    for prop in expected_properties:
        if prop not in actual_properties:
            print(f"❌ Schema missing expected property: {prop}")
            return 1

    print(f"✅ Schema has expected properties: {expected_properties}")
    print("\n✅ All schema verification checks passed!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
