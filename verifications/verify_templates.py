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

"""Verify template files exist and are valid."""

import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
    from generator.filters import markdown_filter, format_datetime_filter
except ImportError as e:
    print(f"✗ FAIL: Could not import dependencies: {e}")
    sys.exit(1)


def main() -> None:
    """Verify all required template files in generator/templates/."""
    templates_dir = Path(__file__).parent.parent / "generator" / "templates"

    if not templates_dir.exists():
        print(f"✗ FAIL: Templates directory not found: {templates_dir}")
        sys.exit(1)

    # Required template files
    required_files = [
        "main.html.jinja",
        "cover.html.jinja",
        "user_story.html.jinja",
        "styles.css",
    ]

    all_passed = True

    print("Verifying required template files exist:")
    for filename in required_files:
        file_path = templates_dir / filename
        if file_path.exists():
            print(f"  ✓ PASS: {filename} exists")
        else:
            print(f"  ✗ FAIL: {filename} not found")
            all_passed = False

    print("\nVerifying template syntax:")
    for filename in required_files:
        if not filename.endswith(".jinja"):
            continue

        file_path = templates_dir / filename
        if not file_path.exists():
            # Already reported above
            continue

        try:
            env = Environment(loader=FileSystemLoader(str(templates_dir)))
            # Register custom filters to avoid "No filter named X" errors
            env.filters["markdown"] = markdown_filter
            env.filters["format_datetime"] = format_datetime_filter
            # Just load the template - this checks syntax without rendering
            env.get_template(filename)
            print(f"  ✓ PASS: {filename} - Valid Jinja2 syntax")
        except TemplateSyntaxError as e:
            print(f"  ✗ FAIL: {filename} - Syntax error: {e}")
            all_passed = False
        except Exception as e:  # pylint: disable=broad-except
            print(f"  ✗ FAIL: {filename} - Unexpected error: {e}")
            all_passed = False

    print("\nVerifying templates reference expected variables:")
    # Check that main template references key schema variables
    main_template_path = templates_dir / "main.html.jinja"
    if main_template_path.exists():
        content = main_template_path.read_text(encoding="utf-8")
        expected_vars = ["meta", "content"]

        for var in expected_vars:
            if var in content:
                print(f"  ✓ PASS: main.html.jinja references '{var}'")
            else:
                print(f"  ✗ FAIL: main.html.jinja does not reference '{var}'")
                all_passed = False

    if all_passed:
        print("\n✓ All template checks passed")
        sys.exit(0)
    else:
        print("\n✗ Some template checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
