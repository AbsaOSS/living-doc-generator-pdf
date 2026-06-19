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

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SelectionSummary(BaseModel):
    """Summary of item selection statistics."""

    total_items: int = Field(ge=0, description="Total number of items")
    included_items: int = Field(ge=0, description="Number of included items")
    excluded_items: int = Field(ge=0, description="Number of excluded items")


class RunContext(BaseModel):
    """Optional CI/CD run context information."""

    ci_run_id: Optional[str] = Field(default=None)
    triggered_by: Optional[str] = Field(default=None)
    branch: Optional[str] = Field(default=None)
    commit_sha: Optional[str] = Field(default=None)


class PdfReadyMetadata(BaseModel):
    """Metadata for the PDF-ready document."""

    document_title: str = Field(
        min_length=1, max_length=200, description="Document title (1-200 characters, non-empty after trimming)"
    )
    document_version: str = Field(
        min_length=1, max_length=50, description="Document version (1-50 characters, semver recommended)"
    )
    generated_at: datetime = Field(description="ISO 8601 UTC timestamp")
    source_set: list[str] = Field(min_length=1, description="Non-empty array of source identifiers")
    selection_summary: SelectionSummary = Field(description="Summary of item selection")
    run_context: Optional[RunContext] = Field(default=None, description="Optional CI/CD run context")


class UserStoryTimestamps(BaseModel):
    """Timestamps for a user story."""

    created: datetime = Field(description="ISO 8601 timestamp")
    updated: datetime = Field(description="ISO 8601 timestamp")


class UserStorySections(BaseModel):
    """Content sections for a user story."""

    description: Optional[str] = Field(default=None, description="Markdown content")
    business_value: Optional[str] = Field(default=None, description="Markdown content")
    preconditions: Optional[str] = Field(default=None, description="Markdown content")
    acceptance_criteria: Optional[str] = Field(default=None, description="Markdown content")
    user_guide: Optional[str] = Field(default=None, description="Markdown content")
    connections: Optional[str] = Field(default=None, description="Markdown content")
    last_edited: Optional[str] = Field(default=None, description="Markdown content")


class UserStory(BaseModel):
    """Represents a single user story in the documentation."""

    id: str = Field(min_length=1, max_length=200, description="Unique canonical stable ID")
    title: str = Field(min_length=1, max_length=500, description="Non-empty title")
    state: str = Field(min_length=1, description="State (e.g., 'open', 'closed')")
    tags: list[str] = Field(description="Array of tags")
    url: str = Field(description="Valid URL (http/https)")
    timestamps: UserStoryTimestamps = Field(description="User story timestamps")
    sections: UserStorySections = Field(description="User story content sections")


class OverviewSummaryStats(BaseModel):
    """Summary statistics for overview section."""

    pass  # Flexible: additional properties allowed


class IndexTable(BaseModel):
    """Index table for overview section."""

    pass  # Flexible: additional properties allowed


class Overview(BaseModel):
    """Optional overview section of the document."""

    summary_stats: Optional[dict] = Field(default=None, description="Summary statistics")
    index_tables: Optional[list[dict]] = Field(default=None, description="Index tables")


class CoverageMatrix(BaseModel):
    """Optional coverage matrix section."""

    version: Optional[str] = Field(default=None, description="Coverage matrix version")
    matrix_data: Optional[list[dict]] = Field(default=None, description="Coverage matrix data")


class PdfReadyContent(BaseModel):
    """Content section of the PDF-ready document."""

    user_stories: list[UserStory] = Field(description="Array of user stories (can be empty)")
    overview: Optional[Overview] = Field(default=None, description="Optional overview section")
    coverage_matrix: Optional[CoverageMatrix] = Field(default=None, description="Optional coverage matrix")


class PdfReadyJson(BaseModel):
    """
    Root model for the PDF-ready JSON format.

    This is the canonical input format for the Living Documentation PDF Generator.
    It represents all necessary documentation data in a source-agnostic structure.
    """

    schema_version: str = Field(
        default="1.0", description="Schema version, must be exactly '1.0'"
    )
    meta: PdfReadyMetadata = Field(description="Document metadata")
    content: PdfReadyContent = Field(description="Document content")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "schema_version": "1.0",
                    "meta": {
                        "document_title": "Living Documentation",
                        "document_version": "1.0.0",
                        "generated_at": "2023-01-15T10:30:00Z",
                        "source_set": ["jira", "github"],
                        "selection_summary": {"total_items": 10, "included_items": 8, "excluded_items": 2},
                    },
                    "content": {"user_stories": []},
                }
            ]
        }
