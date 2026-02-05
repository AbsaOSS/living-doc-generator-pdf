Purpose
- Define consistent, portable rules for this repository's `.github/copilot-instructions.md`.
- Keep rules concrete and testable (a reviewer can verify them).

Structure
- Must keep sections ordered exactly as listed in this file.
- Prefer bullet lists over paragraphs.
- Must write rules as constraints using: Must / Must not / Prefer / Avoid.
- Must end the file with a single blank line.

Context
- Runs as a GitHub Action on GitHub-hosted runners.
- Must read action inputs via `INPUT_*` environment variables.
- Prefer keeping environment access at module boundaries (input layer + entrypoint).

Coding guidelines
- Must keep changes small and focused.
- Prefer clear, explicit code over clever tricks.
- Must keep externally-visible behavior stable unless intentionally updating the contract.
- Must not change existing error messages or log texts without a strong reason (tests may assert exact strings).
- Prefer keeping pure logic free of environment access where practical.

Output discipline (reduce review time)
- Prefer concise final recaps (aim for ≤ 10 lines).
- Avoid restating large file contents/configs/checklists; link and summarize deltas.
- Must end code-change work with:
  - What changed
  - Why
  - How to verify (commands/tests)
- Avoid long rationale, alternatives, or big examples unless explicitly requested.

PR Body Management (optional but recommended)
- Prefer treating the PR description as a changelog and appending updates.
- Must not rewrite/replace the entire PR body when adding new information.
- Prefer this structure:
  - Keep the original description at the top
  - Add updates chronologically below (e.g., `## Update YYYY-MM-DD`)
  - Each update references the commit hash that introduced the change

Inputs (if applicable)
- Must treat inputs as coming from environment variables with the `INPUT_` prefix.
- Must centralize input parsing and validation in a single input layer.
- Avoid duplicating validation logic across modules.

Language and style
- Must target Python 3.14+.
- Must add type hints for new public functions and classes.
- Must use logging (not `print`).
- Must keep Python imports at the top of the file (no imports inside functions/methods).
- Must not disable linter rules inline unless this file documents an allowed exception.

String formatting
- Must use lazy `%` formatting for logging (e.g., `logger.info("msg %s", value)`).
- Must not use f-strings in logging calls.
- Prefer the clearest formatting for exceptions/errors when constructing failure messages.

Docstrings and comments
- Prefer self-explanatory code over comments.
- Prefer comments only for intent, edge cases, and the “why”.
- Docstrings:
  - Prefer a short summary line.
  - Avoid tutorial-style prose and long examples.

Patterns
- Error handling contract:
  - Prefer leaf modules raising exceptions.
  - Must have the entry point translate failures into GitHub Action failure output.
- Internal helpers:
  - Prefer private helpers for internal behavior (e.g., `_helper_name`).
- Testability:
  - Must keep integration boundaries explicit and mockable.
  - Must not call external APIs in unit tests.

Testing
- Must use `pytest` with tests under `tests/`.
- Must not use `unittest` module; use `pytest` and `pytest-mock` exclusively.
- Must test behavior (return values, raised errors, log messages, exit codes).
- Must mock environment variables in unit tests.
- Prefer shared fixtures in `conftest.py`.

Tooling
- Must format with Black (configuration in `pyproject.toml`).
- Must run Pylint on tracked Python files (excluding `tests/`).
- Must run mypy and prefer fixing types over ignoring errors.
- Must run tests with coverage and keep coverage ≥ 80% when enforced.

Quality gates
- Run after changes; fix only if below threshold:
  - Unit tests: `pytest tests/unit/`
  - Full tests (if needed): `pytest tests/`
  - Coverage (minimum 80%): `pytest --ignore=tests/integration --cov=. tests/ --cov-fail-under=80 --cov-report=html`
  - Format: `black $(git ls-files '*.py')`
  - Lint (target ≥ 9.5/10): `pylint --ignore=tests $(git ls-files '*.py')`
  - Types: `mypy .`

Common pitfalls to avoid
- Dependencies: must verify compatibility with the target Python version before adding.
- Logging: must follow lazy `%` formatting; avoid “workarounds”.
- Cleanup: must remove unused imports/variables promptly; avoid dead code.
- Stability: avoid changing externally-visible strings/outputs unless intentional.

Learned rules (optional)
- Must keep error messages stable where tests assert exact strings.
- Must not change exit codes for existing failure scenarios.

Repo additions (required)
- Project name: `Living Doc Generator PDF`.
- Entry points:
  - `main.py` (function `run()`).
  - Input layer: `generator/action_inputs.py` (class `ActionInputs`).
- Inputs (via `INPUT_*` env vars):
  - Required/behavioral: `output-path`, `source-path`.
  - Optional: `template-path`, `document-title`, `verbose`, `github-token`.
- Contract-sensitive outputs:
  - GitHub Action failure strings and log texts (tests may assert exact content).
  - Action output key: `pdf-path`.
- Commands (canonical): see “Quality gates”.
- Allowed exceptions to this template:
  - None.
