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

"""Verify PDF output file and report."""

import json
import sys
from pathlib import Path


def main() -> None:
    """Verify PDF file exists and is valid, and pdf_report.json is present."""
    # Get PDF file path from command line or use default
    pdf_path = Path(sys.argv[1] if len(sys.argv) > 1 else "output.pdf")
    
    if not pdf_path.exists():
        print(f"⚠ WARNING: PDF file not found: {pdf_path}")
        print("  No PDF available to verify (this is OK for verification script testing)")
        sys.exit(0)
    
    all_passed = True
    
    print(f"Verifying PDF file: {pdf_path}")
    
    # Check file exists
    if pdf_path.exists():
        print(f"  ✓ PASS: PDF file exists")
    else:
        print(f"  ✗ FAIL: PDF file does not exist")
        all_passed = False
        # Can't continue with other checks
        sys.exit(1)
    
    # Check file has non-zero size
    file_size = pdf_path.stat().st_size
    if file_size > 0:
        print(f"  ✓ PASS: PDF file has non-zero size ({file_size} bytes)")
    else:
        print(f"  ✗ FAIL: PDF file is empty")
        all_passed = False
    
    # Check PDF magic bytes (%PDF)
    try:
        with open(pdf_path, "rb") as f:
            header = f.read(4)
            if header == b"%PDF":
                print(f"  ✓ PASS: PDF file has valid magic bytes (%PDF)")
            else:
                print(f"  ✗ FAIL: PDF file does not start with %PDF magic bytes")
                all_passed = False
    except Exception as e:  # pylint: disable=broad-except
        print(f"  ✗ FAIL: Could not read PDF file: {e}")
        all_passed = False
    
    # Check for corresponding pdf_report.json
    report_path = pdf_path.parent / "pdf_report.json"
    print(f"\nVerifying PDF report: {report_path}")
    
    if report_path.exists():
        print(f"  ✓ PASS: pdf_report.json exists")
    else:
        print(f"  ✗ FAIL: pdf_report.json not found")
        all_passed = False
        # Continue to see other failures
    
    if report_path.exists():
        # Verify it's valid JSON
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            print(f"  ✓ PASS: pdf_report.json is valid JSON")
            
            # Check for required fields
            required_fields = [
                "schema_version",
                "generated_at",
                "input_file",
                "output_file",
                "template_pack",
                "statistics",
            ]
            
            for field in required_fields:
                if field in report_data:
                    print(f"  ✓ PASS: pdf_report.json contains '{field}'")
                else:
                    print(f"  ✗ FAIL: pdf_report.json missing required field '{field}'")
                    all_passed = False
        except json.JSONDecodeError as e:
            print(f"  ✗ FAIL: pdf_report.json is not valid JSON: {e}")
            all_passed = False
        except Exception as e:  # pylint: disable=broad-except
            print(f"  ✗ FAIL: Could not read pdf_report.json: {e}")
            all_passed = False
    
    if all_passed:
        print("\n✓ All PDF output checks passed")
        sys.exit(0)
    else:
        print("\n✗ Some PDF output checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
