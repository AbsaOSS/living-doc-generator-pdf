# Copilot Review Rules — Living Doc Generator PDF

This file defines how Copilot reviews pull requests in this repository. It describes this
repo's own risk areas and review expectations; it is not shared with other repos.

**House rules for this file**

- Must write every guidance bullet as a constraint led by one of `Must`, `Must not`, `Prefer`, `Avoid`.
- Must not put a colon after the leading keyword, and Must not use any other keyword style.
- Prefer short headings and bullet lists over prose.
- Prefer verifiable checks — a reviewer can point to the code and the impact.
- Avoid long audit reports unless they are explicitly requested.

## Review modes

- Must support two modes — Default review for standard PR risk, and Double-check review for elevated-risk PRs.

## Mode — Default review

- Must treat the change as a single PR with normal risk.
- Must prioritise in this order — correctness, security, tests, maintainability, style.

**Checks**

- Must flag logic bugs, missing edge cases, regressions, and unintended contract changes.
- Must flag unsafe input handling, secret exposure, and insecure defaults.
- Must check that tests exist for changed logic and cover the success and failure paths.
- Prefer calling out unnecessary complexity, duplication, and unclear naming or structure.
- Avoid style notes unless they reduce readability or break a repo convention.

**Response format**

- Must use short bullet points.
- Prefer referencing files and line ranges.
- Must group comments by severity — Blocker (must fix), Important (should fix), Nit (optional).
- Prefer actionable suggestions over rewrites.
- Must not rewrite the whole PR or produce a long report.

## Mode — Double-check review

- Must treat the change as higher risk — security, infra, wide refactors, data or schema migrations, changes to the input contract or exit codes.

**Additional focus**

- Prefer confirming that previous review comments were addressed correctly.
- Must re-check high-risk areas — input parsing, filesystem writes, external calls, error-to-exit-code mapping, schema validation.
- Prefer looking for hidden side effects — backward compatibility, failure modes, behaviour on missing or malformed inputs.
- Prefer validating safe defaults — least privilege, safe error messages, predictable behaviour when an input is absent.

**Response format**

- Prefer commenting only where risk or impact is non-trivial.
- Avoid repeating minor style notes already covered by Default review.
- Prefer stating risk acceptance explicitly when something is left as-is — the risk, why it is acceptable, and the mitigation that exists.

## Commenting rules — all modes

- Must include for every comment — what the issue is (one line), why it matters (impact or risk), and how to fix it (a minimal actionable suggestion).
- Prefer linking to an existing pattern in the repo over introducing a new one.
- Must ask a targeted question instead of assuming when context is missing.

## Non-goals

- Must not request refactors unrelated to the PR's intent.
- Must not bikeshed formatting that Black or Pylint already enforces.
- Avoid proposing architectural rewrites unless they are explicitly requested.

## Repo specifics

- Must treat these as high-risk areas — `INPUT_*` parsing in `generator/action_inputs.py`, filesystem writes, the render and PDF pipeline in `main.run()`, and JSON Schema validation in `generator/schema_validator.py`.
- Must treat these as contract-sensitive — exact failure strings, exit codes `1`–`5`, the Action output keys `pdf-path` / `html-path` / `report-path`, and the `<pdf-stem>_rendered.html` debug filename. Tests assert exact content.
- Must expect unit tests under `tests/unit/` and integration tests under `tests/integration/`.
- Must expect QA to run through the root `Makefile` — `make qa` covers `format-check`, `lint`, `types`, and `test`.
