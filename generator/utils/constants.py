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

# Living-doc PDF inputs (temporary contract)
SOURCE_PATH = "source-path"
TEMPLATE_PATH = "template-path"
DOCUMENT_TITLE = "document-title"
OUTPUT_PATH = "output-path"
