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

"""Verify all example JSON files against the schema."""

import sys
from pathlib import Path

try:
    from generator.schema_validator import SchemaValidationError, validate_pdf_ready_json
except ImportError as e:
    print(f"✗ FAIL: Could not import schema validator: {e}")
    sys.exit(1)


def main() -> None:
    """Validate all example JSON files in examples/ directory."""
    examples_dir = Path(__file__).parent.parent / "examples"
    
    if not examples_dir.exists():
        print(f"✗ FAIL: Examples directory not found: {examples_dir}")
        sys.exit(1)
    
    # Files that should pass validation
    valid_examples = [
        "minimal_valid.json",
        "full_example.json",
        "multiple_stories.json",
    ]
    
    # Files that should fail validation
    invalid_examples = [
        "invalid_missing_schema.json",
        "invalid_bad_timestamp.json",
    ]
    
    all_passed = True
    
    print("Verifying valid example files:")
    for filename in valid_examples:
        file_path = examples_dir / filename
        if not file_path.exists():
            print(f"  ✗ FAIL: {filename} - File not found")
            all_passed = False
            continue
        
        try:
            validate_pdf_ready_json(str(file_path))
            print(f"  ✓ PASS: {filename}")
        except SchemaValidationError as e:
            print(f"  ✗ FAIL: {filename} - Validation failed: {e}")
            all_passed = False
        except Exception as e:  # pylint: disable=broad-except
            print(f"  ✗ FAIL: {filename} - Unexpected error: {e}")
            all_passed = False
    
    print("\nVerifying invalid example files:")
    for filename in invalid_examples:
        file_path = examples_dir / filename
        if not file_path.exists():
            print(f"  ✗ FAIL: {filename} - File not found")
            all_passed = False
            continue
        
        try:
            validate_pdf_ready_json(str(file_path))
            print(f"  ✗ FAIL: {filename} - Should have failed validation but passed")
            all_passed = False
        except SchemaValidationError:
            print(f"  ✓ PASS: {filename} - Correctly rejected")
        except Exception as e:  # pylint: disable=broad-except
            print(f"  ✗ FAIL: {filename} - Unexpected error: {e}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All schema validation checks passed")
        sys.exit(0)
    else:
        print("\n✗ Some schema validation checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
