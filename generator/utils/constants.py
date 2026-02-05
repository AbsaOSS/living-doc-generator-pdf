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

"""Shared constant names for GitHub Action inputs.

Inputs are read from `INPUT_*` environment variables using
`generator.utils.gh_action.get_action_input`.
"""

# Common action inputs
GITHUB_TOKEN = "github-token"
VERBOSE = "verbose"

# New PDF-ready JSON inputs
PDF_READY_JSON = "pdf-ready-json"
OUTPUT_PATH = "output-path"
TEMPLATE_DIR = "template-dir"
DEBUG_HTML = "debug-html"

# Legacy inputs (deprecated - to be removed in v2.0)
SOURCE_PATH = "source-path"  # Deprecated
TEMPLATE_PATH = "template-path"  # Deprecated
DOCUMENT_TITLE = "document-title"  # Deprecated
