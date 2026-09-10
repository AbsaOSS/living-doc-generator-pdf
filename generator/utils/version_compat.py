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

"""Portable input schema-version compatibility check.

This helper mirrors the ``living-doc-toolkit`` adapter pattern: a canonical
source document declares a ``schema_version`` and the consumer checks it against
a supported semver range. An out-of-range but parseable version produces a
captured warning and rendering still proceeds; every other case — the key
missing, an explicit JSON ``null``, a non-string value, a blank string, or an
unparseable value — is a hard error with a single structured message (exit code 1).

The module has no PDF-specific dependencies so other generators (for example a
future Markdown generator) can reuse it verbatim.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Optional

import semver

logger = logging.getLogger(__name__)

# Sentinel so callers can distinguish "key absent" from an explicit JSON ``null``.
# Both are treated identically (hard error), but keeping the distinction lets the
# caller pass ``data.get("schema_version", MISSING)`` without ambiguity.
MISSING: Any = object()

# Supported range for the canonical input schema: any 1.x version.
SUPPORTED_SCHEMA_RANGE_MIN = "1.0.0"
SUPPORTED_SCHEMA_RANGE_MAX = "2.0.0"
SUPPORTED_SCHEMA_RANGE = f">={SUPPORTED_SCHEMA_RANGE_MIN},<{SUPPORTED_SCHEMA_RANGE_MAX}"

# ``schema_version`` values look like ``generator-ready-v1.0.0`` or a bare
# ``1.0`` / ``1.0.0``, optionally with a SemVer pre-release / build suffix
# (``generator-ready-v1.5.0-rc.1``). Capture the trailing version token.
_VERSION_TOKEN_RE = re.compile(
    r"(?:^|[-_/]v?)(\d+(?:\.\d+){0,2}(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?)$"
)


class VersionCompatibilityError(ValueError):
    """Raised when ``schema_version`` is absent, null, non-string, blank, or unparseable (exit code 1)."""


@dataclass(frozen=True)
class CompatibilityWarning:
    """A non-fatal compatibility finding, shaped like the toolkit warning schema."""

    code: str
    message: str
    context: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Return the warning as a plain dict for the report ``warnings`` list."""
        return {"code": self.code, "message": self.message, "context": self.context}


def _coerce_semver(token: str) -> semver.Version:
    """Parse a 1-to-3 component dotted-number token, with an optional SemVer
    pre-release / build suffix, into a full semver Version."""
    core, sep, suffix = token.partition("-")
    build = ""
    if "+" in (suffix if sep else core):
        base, _, build = (suffix if sep else core).partition("+")
        if sep:
            suffix = base
        else:
            core, suffix = base, ""
    parts = core.split(".")
    while len(parts) < 3:
        parts.append("0")
    normalized = ".".join(parts)
    if sep and suffix:
        normalized += f"-{suffix}"
    if build:
        normalized += f"+{build}"
    return semver.Version.parse(normalized)


def check_schema_version(schema_version: Any = MISSING) -> list[CompatibilityWarning]:
    """Check a source document's ``schema_version`` against the supported range.

    Args:
        schema_version: The raw ``schema_version`` value from the source JSON.
            Pass :data:`MISSING` (the default) when the key is absent, ``None``
            for an explicit JSON ``null``.

    Returns:
        A list of :class:`CompatibilityWarning`: empty when the version is in
        range, one ``schema_version_out_of_range`` warning when it parses but
        falls outside :data:`SUPPORTED_SCHEMA_RANGE`.

    Raises:
        VersionCompatibilityError: When ``schema_version`` is absent, ``null``,
            not a string, blank, or does not contain a parseable version token.
            The exception message is a single structured line (exit code 1).
    """
    _expected = f"Expected a semantic version in range {SUPPORTED_SCHEMA_RANGE} (for example 'generator-ready-v1.0.0')."

    if schema_version is MISSING or schema_version is None:
        state = "absent" if schema_version is MISSING else "null"
        raise VersionCompatibilityError(
            f"Invalid input: 'schema_version' is {state}. Every source document must "
            f"declare which input contract it targets. {_expected}"
        )

    if not isinstance(schema_version, str):
        raise VersionCompatibilityError(
            f"Invalid input: 'schema_version' must be a string, got {type(schema_version).__name__}. {_expected}"
        )

    raw = schema_version.strip()
    if not raw:
        raise VersionCompatibilityError(f"Invalid input: 'schema_version' is present but blank. {_expected}")

    match = _VERSION_TOKEN_RE.search(raw)
    if not match:
        raise VersionCompatibilityError(f"Invalid input: unparseable 'schema_version' value {raw!r}. {_expected}")

    try:
        version = _coerce_semver(match.group(1))
    except ValueError as exc:
        raise VersionCompatibilityError(
            f"Invalid input: unparseable 'schema_version' value {raw!r}. {_expected}"
        ) from exc

    lower = semver.Version.parse(SUPPORTED_SCHEMA_RANGE_MIN)
    upper = semver.Version.parse(SUPPORTED_SCHEMA_RANGE_MAX)
    # Compare on the released (core) version so a pre-release such as
    # ``1.5.0-rc.1`` is judged by its ``1.5.0`` target, not ranked below it.
    core_version = version.finalize_version()
    if core_version < lower or core_version >= upper:
        message = (
            f"Source 'schema_version' {raw!r} (parsed as {version}) is outside the "
            f"supported range {SUPPORTED_SCHEMA_RANGE}; attempting to render anyway."
        )
        logger.warning(message)
        return [CompatibilityWarning(code="schema_version_out_of_range", message=message, context=raw)]

    logger.info("Source 'schema_version' %r is within the supported range %s.", raw, SUPPORTED_SCHEMA_RANGE)
    return []
