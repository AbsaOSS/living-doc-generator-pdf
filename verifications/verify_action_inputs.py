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

"""Verify that ActionInputs has all required methods and constants are defined."""

import inspect
import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.action_inputs import ActionInputs  # noqa: E402
from generator.utils import constants  # noqa: E402


def main() -> int:
    """Verify all input methods exist and have correct signatures."""
    # Define expected methods and their signatures
    expected_methods = {
        "get_pdf_ready_json": {"return": str, "params": []},
        "get_output_path": {"return": str, "params": []},
        "get_template_dir": {"return": "Optional[str]", "params": []},
        "get_debug_html": {"return": bool, "params": []},
        "get_verbose": {"return": bool, "params": []},
    }

    # Check each method exists
    for method_name, expected in expected_methods.items():
        if not hasattr(ActionInputs, method_name):
            print(f"❌ Missing method: ActionInputs.{method_name}")
            return 1

        method = getattr(ActionInputs, method_name)
        if not callable(method):
            print(f"❌ {method_name} is not callable")
            return 1

        print(f"✅ Method exists: ActionInputs.{method_name}")

    # Check constants are defined
    expected_constants = [
        "PDF_READY_JSON",
        "OUTPUT_PATH",
        "TEMPLATE_DIR",
        "DEBUG_HTML",
        "VERBOSE",
    ]

    for const_name in expected_constants:
        if not hasattr(constants, const_name):
            print(f"❌ Missing constant: {const_name}")
            return 1
        print(f"✅ Constant defined: {const_name}")

    print("\n✅ All ActionInputs verification checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
