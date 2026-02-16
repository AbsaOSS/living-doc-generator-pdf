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


@pytest.fixture
def examples_dir() -> Path:
    """Return the path to the examples directory."""
    return Path(__file__).parent.parent.parent / "examples"


@pytest.fixture
def minimal_valid_json(examples_dir: Path) -> Path:
    """Return the path to minimal_valid.json example."""
    return examples_dir / "minimal_valid.json"


@pytest.fixture
def full_example_json(examples_dir: Path) -> Path:
    """Return the path to full_example.json example."""
    return examples_dir / "full_example.json"


@pytest.fixture
def multiple_stories_json(examples_dir: Path) -> Path:
    """Return the path to multiple_stories.json example."""
    return examples_dir / "multiple_stories.json"


@pytest.fixture
def invalid_missing_schema_json(examples_dir: Path) -> Path:
    """Return the path to invalid_missing_schema.json example."""
    return examples_dir / "invalid_missing_schema.json"


@pytest.fixture
def invalid_bad_timestamp_json(examples_dir: Path) -> Path:
    """Return the path to invalid_bad_timestamp.json example."""
    return examples_dir / "invalid_bad_timestamp.json"


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir
