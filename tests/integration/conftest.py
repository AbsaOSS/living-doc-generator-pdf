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

"""Shared fixtures for integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture
def examples_dir() -> Path:
    """Return the path to the examples directory."""
    return _REPO_ROOT / "examples"


@pytest.fixture
def schemas_dir() -> Path:
    """Return the path to the built-in schemas directory."""
    return _REPO_ROOT / "generator" / "schemas"


@pytest.fixture
def minimal_json(examples_dir: Path) -> Path:
    """Return the path to the minimal user-stories example."""
    return examples_dir / "minimal.json"


@pytest.fixture
def user_stories_json(examples_dir: Path) -> Path:
    """Return the path to the user-stories example."""
    return examples_dir / "user_stories.json"


@pytest.fixture
def ui_tests_json(examples_dir: Path) -> Path:
    """Return the path to the ui-test-catalog example."""
    return examples_dir / "ui_tests.json"


@pytest.fixture
def coverage_matrix_json(examples_dir: Path) -> Path:
    """Return the path to the coverage-matrix example."""
    return examples_dir / "coverage_matrix.json"


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir
