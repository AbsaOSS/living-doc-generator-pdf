# Copilot Review Rules

Purpose
- Define consistent review behavior and response formatting for Copilot code reviews across repositories.
- Prefer repository-specific additions to be short and appended in “Repo additions”.

Writing style
- Prefer short headings and bullet lists.
- Prefer do/avoid constraints over prose.
- Prefer verifiable checks (reviewer can point to code + impact).
- Avoid long audit reports unless explicitly requested.

Review modes
- Must support two modes:
  - Default review: standard PR risk.
  - Double-check review: elevated risk PRs.

Mode: Default review
- Scope
  - Must treat as a single PR with normal risk.
- Priorities (in order)
  - Must prioritize: correctness → security → tests → maintainability → style.
- Checks
  - Correctness
    - Must highlight logic bugs, missing edge cases, regressions, and unintended contract changes.
  - Security & data handling
    - Must flag unsafe input handling, secrets exposure, auth/authz issues, and insecure defaults.
  - Tests
    - Must check tests exist for changed logic and cover success + failure paths.
  - Maintainability
    - Prefer calling out unnecessary complexity, duplication, and unclear naming/structure.
  - Style
    - Avoid style notes unless they reduce readability or break repo conventions.
- Response format
  - Must use short bullet points.
  - Prefer referencing files + line ranges where possible.
  - Must group comments by severity:
    - Blocker (must fix), Important (should fix), Nit (optional).
  - Prefer actionable suggestions (what to change) over rewrites.
  - Must not rewrite the whole PR or produce long reports.

Mode: Double-check review
- Scope
  - Must treat as higher-risk PRs (security, infra, money flows, wide refactors, data migrations, auth changes).
- Additional focus
  - Prefer confirming previous review comments were correctly addressed (when applicable).
  - Must re-check high-risk areas:
    - auth, permissions, secrets, money transfers/billing, persistence, external calls, concurrency.
  - Prefer looking for hidden side effects:
    - backward compatibility, rollout/upgrade path, failure modes, retries/timeouts, idempotency.
  - Prefer validating safe defaults:
    - least privilege, secure logging, safe error messages, predictable behavior on missing inputs.
- Response format
  - Prefer adding comments only where risk/impact is non-trivial.
  - Avoid repeating minor style notes already covered by default review.
  - Prefer calling out “risk acceptance” explicitly if something is left as-is:
    - what risk, why acceptable, what mitigation exists (tests/monitoring/feature flag).

Commenting rules (applies to all modes)
- Must include for each comment:
  - What is the issue (1 line).
  - Why it matters (impact/risk).
  - How to fix (minimal actionable suggestion).
- Prefer linking to existing patterns in the repo over introducing new ones.
- If context is missing, must ask a targeted question instead of assuming.

Non-goals
- Must not request refactors unrelated to the PR’s intent.
- Must not bikeshed formatting if tools (formatter/linter) handle it.
- Avoid proposing architectural rewrites unless explicitly requested.

Repo additions (keep short)
- Domain-specific high-risk areas:
  - GitHub Action input parsing (`INPUT_*`), filesystem writes, PDF generation pipeline.
- Contract-sensitive outputs:
  - Exact failure strings / log texts and exit-code behavior (tests may assert exact content).
- Required test types and location:
  - Unit tests under `tests/unit/`.
