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

from pathlib import Path

# Common action inputs
GITHUB_TOKEN = "github-token"
VERBOSE = "verbose"

# Source and rendering inputs
SOURCE_PATH = "source-path"
TEMPLATE_PATH = "template-path"
DOCUMENT_TYPE = "document-type"
SCHEMA_PATH = "schema-path"
OUTPUT_PATH = "output-path"
DEBUG_HTML = "debug-html"
DOCUMENT_TITLE = "document-title"

# Deprecated alias for SOURCE_PATH (kept through the next major release)
PDF_READY_JSON = "pdf-ready-json"

# Built-in document types and their default titles
DOCUMENT_TYPE_TECHNICAL_PROJECT = "technical-project"
DOCUMENT_TYPE_UI_TEST_CATALOG = "ui-test-catalog"
DOCUMENT_TYPE_COVERAGE_MATRIX = "coverage-matrix"

DOCUMENT_TYPES = (
    DOCUMENT_TYPE_TECHNICAL_PROJECT,
    DOCUMENT_TYPE_UI_TEST_CATALOG,
    DOCUMENT_TYPE_COVERAGE_MATRIX,
)

DEFAULT_DOCUMENT_TITLES = {
    DOCUMENT_TYPE_TECHNICAL_PROJECT: "Technical Project",
    DOCUMENT_TYPE_UI_TEST_CATALOG: "UI Test Catalog",
    DOCUMENT_TYPE_COVERAGE_MATRIX: "Coverage Matrix",
}

# Maps logical document types to the template directory they use.
DOCUMENT_TYPE_TEMPLATE_DIR = {
    DOCUMENT_TYPE_TECHNICAL_PROJECT: DOCUMENT_TYPE_TECHNICAL_PROJECT,
    DOCUMENT_TYPE_UI_TEST_CATALOG: DOCUMENT_TYPE_UI_TEST_CATALOG,
    DOCUMENT_TYPE_COVERAGE_MATRIX: DOCUMENT_TYPE_COVERAGE_MATRIX,
}

# Vendored input schemas, one per built-in document type. Each is a pinned copy
# of the owning repo's generated file; see ``generator/schemas/README.md`` for
# the pin locations.
_SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"

GENERATOR_READY_SCHEMA_FILENAME = "generator-ready-v1.0.0-schema.json"
UI_TESTS_SCHEMA_FILENAME = "ui-tests-v1.0.0-schema.json"
COVERAGE_MATRIX_SCHEMA_FILENAME = "coverage-matrix-v1.0.0-schema.json"

DEFAULT_GENERATOR_READY_SCHEMA_PATH = str(_SCHEMAS_DIR / GENERATOR_READY_SCHEMA_FILENAME)

# Structural-validation schema applied by default for each built-in document
# type when the caller passes no explicit ``schema-path``. Every built-in type
# validates its source against a vendored schema out of the box; an explicit
# ``schema-path`` always overrides the default.
DOCUMENT_TYPE_DEFAULT_SCHEMA = {
    DOCUMENT_TYPE_TECHNICAL_PROJECT: DEFAULT_GENERATOR_READY_SCHEMA_PATH,
    DOCUMENT_TYPE_UI_TEST_CATALOG: str(_SCHEMAS_DIR / UI_TESTS_SCHEMA_FILENAME),
    DOCUMENT_TYPE_COVERAGE_MATRIX: str(_SCHEMAS_DIR / COVERAGE_MATRIX_SCHEMA_FILENAME),
}
