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

"""Unit tests for the document metadata model."""

import re

from generator.models import Meta, build_meta

_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def test_build_meta_sets_source_basename() -> None:
    """build_meta exposes only the basename of the source file."""
    meta = build_meta("My Title", "/path/to/data.json")
    assert meta.source_file == "data.json"
    assert meta.document_title == "My Title"


def test_build_meta_generated_at_is_iso_utc() -> None:
    """build_meta produces an ISO 8601 UTC timestamp ending in Z."""
    meta = build_meta("T", "data.json")
    assert _ISO_RE.match(meta.generated_at)


def test_meta_to_dict_exposes_template_fields() -> None:
    """to_dict returns exactly the fields exposed to templates."""
    meta = Meta(document_title="T", generated_at="2024-01-01T00:00:00Z", source_file="data.json")
    assert meta.to_dict() == {
        "document_title": "T",
        "generated_at": "2024-01-01T00:00:00Z",
        "source_file": "data.json",
    }


def test_meta_is_frozen() -> None:
    """Meta instances are immutable."""
    meta = build_meta("T", "data.json")
    try:
        meta.document_title = "other"  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("Meta should be immutable")
