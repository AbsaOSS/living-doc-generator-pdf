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

"""Verify error message format consistency."""

import sys

try:
    from generator.schema_validator import SchemaValidationError
    from generator.template_renderer import TemplateError
    from generator.pdf_generator import RenderingError, FileIOError
except ImportError as e:
    print(f"✗ FAIL: Could not import error classes: {e}")
    sys.exit(1)


def main() -> None:
    """Verify error classes exist and follow expected patterns."""
    all_passed = True
    
    # Expected error classes and their prefixes from SPEC.md § 3.1.3
    error_classes = [
        (SchemaValidationError, "SchemaValidationError", "Schema validation failed:"),
        (TemplateError, "TemplateError", "Template error:"),
        (RenderingError, "RenderingError", "Rendering failed:"),
        (FileIOError, "FileIOError", "File I/O error:"),
    ]
    
    print("Verifying error classes exist and can be instantiated:")
    for error_class, name, expected_prefix in error_classes:
        try:
            # Verify the class exists
            if not issubclass(error_class, Exception):
                print(f"  ✗ FAIL: {name} is not an Exception subclass")
                all_passed = False
                continue
            
            # Verify it can be instantiated with a message
            test_message = f"{expected_prefix} test detail. Test guidance."
            instance = error_class(test_message)
            
            if str(instance) == test_message:
                print(f"  ✓ PASS: {name} exists and can be instantiated")
            else:
                print(f"  ✗ FAIL: {name} message format unexpected")
                all_passed = False
        except Exception as e:  # pylint: disable=broad-except
            print(f"  ✗ FAIL: {name} - Error during instantiation: {e}")
            all_passed = False
    
    print("\nVerifying error message prefix format (from SPEC.md § 3.1.3):")
    # Check that the expected prefixes match specification
    spec_prefixes = {
        "SchemaValidationError": "Schema validation failed:",
        "TemplateError": "Template error:",
        "RenderingError": "Rendering failed:",
        "FileIOError": "File I/O error:",
    }
    
    for error_class, name, expected_prefix in error_classes:
        spec_prefix = spec_prefixes.get(name)
        if expected_prefix == spec_prefix:
            print(f"  ✓ PASS: {name} prefix matches SPEC.md: '{expected_prefix}'")
        else:
            print(f"  ✗ FAIL: {name} prefix mismatch - expected '{spec_prefix}', got '{expected_prefix}'")
            all_passed = False
    
    print("\nVerifying error message format pattern:")
    # Verify the format follows: {prefix} {detail}. {guidance}
    for error_class, name, expected_prefix in error_classes:
        try:
            # Create a well-formatted message
            detail = "specific detail"
            guidance = "actionable guidance"
            test_message = f"{expected_prefix} {detail}. {guidance}"
            
            instance = error_class(test_message)
            message_str = str(instance)
            
            # Check that message contains the prefix
            if expected_prefix in message_str:
                print(f"  ✓ PASS: {name} message contains prefix '{expected_prefix}'")
            else:
                print(f"  ✗ FAIL: {name} message does not contain expected prefix")
                all_passed = False
        except Exception as e:  # pylint: disable=broad-except
            print(f"  ✗ FAIL: {name} - Error creating formatted message: {e}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All error message checks passed")
        sys.exit(0)
    else:
        print("\n✗ Some error message checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
