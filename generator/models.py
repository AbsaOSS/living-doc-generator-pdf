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

"""
Pydantic models for pdf_ready.json input format.

These models represent the authoritative contract for the PDF-ready JSON format.
They are the single source of truth for the schema between this repository
(schema producer / data consumer) and upstream living doc systems
(data producer / schema consumer).

PYDANTIC-FIRST PATTERN
======================

This repo:
- Defines Pydantic models for the input contract (source of truth)
- Exports them as JSON Schema for upstream systems to use for validation

Upstream systems:
- Use our exported JSON Schema to validate pdf_ready.json
- Publish validated data to this repo

To export schema for upstream systems:
    python -m generator.schema_export > pdf_ready-schema.json

See SCHEMA_SYNC.md for the full synchronization workflow.
"""

from typing import Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Audit envelope
# ---------------------------------------------------------------------------


class Producer(BaseModel):
    """Producer metadata."""

    name: str = Field(description="Producer name")
    version: str = Field(description="Producer version")
    build: Optional[str] = Field(default=None)

    model_config = {"extra": "forbid"}


class Run(BaseModel):
    """Run metadata."""

    run_id: Optional[str] = Field(default=None)
    run_attempt: Optional[str] = Field(default=None)
    actor: Optional[str] = Field(default=None)
    workflow: Optional[str] = Field(default=None)
    ref: Optional[str] = Field(default=None)
    sha: Optional[str] = Field(default=None)

    model_config = {"extra": "forbid"}


class Source(BaseModel):
    """Source metadata."""

    systems: list[str] = Field(description="Source systems")
    organization: Optional[str] = Field(default=None)
    enterprise: Optional[str] = Field(default=None)
    repositories: list[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class Warning(BaseModel):
    """Warning in trace step."""

    code: str = Field(description="Warning code")
    message: str = Field(description="Human-readable message")
    context: Optional[str] = Field(default=None)

    model_config = {"extra": "forbid"}


class TraceStep(BaseModel):
    """Trace step in audit trail."""

    step: str = Field(description="Step name")
    tool: str = Field(description="Tool name")
    tool_version: str = Field(description="Tool version")
    started_at: Optional[str] = Field(default=None)
    finished_at: Optional[str] = Field(default=None)
    warnings: list[Warning] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class AuditEnvelopeV1(BaseModel):
    """Audit envelope v1.0."""

    schema_version: str = Field(description="Schema version")
    producer: Producer
    run: Run
    source: Source
    trace: list[TraceStep] = Field(default_factory=list)
    extensions: dict = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


class SelectionSummary(BaseModel):
    """Selection summary."""

    total_items: int = Field(ge=0, description="Total items")
    included_items: int = Field(ge=0, description="Included items")
    excluded_items: int = Field(ge=0, description="Excluded items")

    model_config = {"extra": "forbid"}


class RunContext(BaseModel):
    """Optional CI/CD run context information."""

    ci_run_id: Optional[str] = Field(default=None)
    triggered_by: Optional[str] = Field(default=None)
    branch: Optional[str] = Field(default=None)
    commit_sha: Optional[str] = Field(default=None)

    model_config = {"extra": "forbid"}


class Meta(BaseModel):
    """Metadata section."""

    document_title: str = Field(min_length=1, max_length=200, description="Document title")
    document_version: str = Field(min_length=1, max_length=50, description="Document version")
    generated_at: str = Field(description="ISO 8601 UTC timestamp")
    source_set: list[str] = Field(min_length=1, description="Non-empty array of source identifiers")
    selection_summary: SelectionSummary
    run_context: Optional[RunContext] = Field(default=None)
    audit: Optional[AuditEnvelopeV1] = Field(default=None)

    model_config = {"extra": "forbid"}


# ---------------------------------------------------------------------------
# User story
# ---------------------------------------------------------------------------


class Timestamps(BaseModel):
    """Timestamps for a user story."""

    created: str = Field(description="ISO 8601 timestamp")
    updated: str = Field(description="ISO 8601 timestamp")

    model_config = {"extra": "forbid"}


class AcceptanceCriterion(BaseModel):
    """A single acceptance criterion entry."""

    description: str = Field(description="Criterion text")
    id: Optional[str] = Field(default=None, description="Criterion identifier")
    state: Optional[str] = Field(default=None, description="State (e.g. 'Active')")
    version: Optional[str] = Field(default=None, description="Version when introduced")

    model_config = {"extra": "forbid"}


class Sections(BaseModel):
    """Content sections for a user story."""

    description: Optional[str] = Field(default=None, description="Markdown content")
    business_value: Optional[list[str]] = Field(default=None, description="Business value items")
    preconditions: Optional[list[str]] = Field(default=None, description="Precondition items")
    acceptance_criteria: Optional[list[AcceptanceCriterion]] = Field(default=None, description="Acceptance criteria")
    user_guide: Optional[str] = Field(default=None, description="Markdown content")
    connections: Optional[str] = Field(default=None, description="Markdown content")
    last_edited: Optional[str] = Field(default=None, description="Markdown content")

    model_config = {"extra": "forbid"}


class UserStory(BaseModel):
    """Represents a single user story in the documentation."""

    id: str = Field(description="Canonical stable ID")
    title: str = Field(min_length=1, max_length=500, description="Non-empty title")
    state: str = Field(description="State (e.g., 'open', 'closed')")
    tags: list[str] = Field(description="Array of tags")
    url: str = Field(description="Valid URL")
    timestamps: Timestamps
    sections: Sections

    model_config = {"extra": "forbid"}


# ---------------------------------------------------------------------------
# Content & root
# ---------------------------------------------------------------------------


class Content(BaseModel):
    """Content section."""

    user_stories: list[UserStory] = Field(description="List of user stories")

    model_config = {"extra": "forbid"}


class PdfReadyV1(BaseModel):
    """Root model for the PDF-ready JSON format (v1.0)."""

    schema_version: str = Field(description="Schema version, must be '1.0'")
    meta: Meta
    content: Content

    model_config = {"extra": "forbid"}


# Backwards-compatible alias
PdfReadyJson = PdfReadyV1
