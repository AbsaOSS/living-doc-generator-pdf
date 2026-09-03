# Copilot Instructions — Living Doc Generator PDF

This file tells a coding agent how to work in this repository. It describes this repo's
own layout, contract, and workflow; it is not shared with or copied from other repos.

**Section order** — keep the sections below in exactly this order:
Overview → Repo specifics → Coding guidelines → Inputs → Language and style →
Logging and string formatting → Docstrings and comments → Patterns → Testing →
Tooling and quality gates → Common pitfalls → Learned rules.

**House rules for this file**

- Must write every guidance bullet as a constraint led by one of `Must`, `Must not`, `Prefer`, `Avoid`.
- Must not put a colon after the leading keyword, and Must not use any other keyword style such as `Do`, `Should`, or a two-keyword `Do` / `Avoid` variant.
- Prefer bullet lists over paragraphs.
- Must end the file with a single trailing newline.

## Overview

`Living Doc Generator PDF` is a composite GitHub Action that renders a canonical source
JSON file into a PDF using Jinja2 templates and WeasyPrint.

- Must treat execution as a GitHub Action on a GitHub-hosted runner as the supported path; the `run_locally.sh` / `python main.py` flow is a development and debugging affordance only.
- Must read action inputs from `INPUT_*` environment variables and nowhere else.
- Prefer keeping environment access at the module boundary — the input layer and the entry point — and Must keep the render and PDF pipeline free of environment reads.

## Repo specifics

Module map — the `generator/` package:

| Path | Responsibility |
|---|---|
| `generator/action_inputs.py` | Input layer — class `ActionInputs`, reads every `INPUT_*` var, `validate_inputs()` |
| `generator/schema_validator.py` | `load_source()`, optional JSON Schema validation, raises `SchemaValidationError` |
| `generator/models.py` | `build_meta()` and the per-document data structures |
| `generator/template_renderer.py` | `TemplateRenderer` — resolves built-in vs custom template packs, raises `TemplateError` |
| `generator/filters.py` | Jinja2 filters used by the templates |
| `generator/pdf_generator.py` | `PdfGenerator` — HTML to PDF via WeasyPrint, raises `RenderingError` / `FileIOError` |
| `generator/report_generator.py` | `generate_pdf_report()` — writes `pdf_report.json` |
| `generator/schemas/` | Bundled `*-v1.0.0-schema.json` files |
| `generator/templates/` | Built-in template packs — `user-stories/`, `ui-test-catalog/`, `coverage-matrix/` |
| `generator/utils/` | `constants.py`, `enums.py`, `gh_action.py`, `logging_config.py`, `decorators.py` |

- Must treat `main.py` function `run()` as the entry point — it orchestrates validate inputs → load source (optional schema validation) → resolve template set → render HTML → optional debug HTML → generate PDF → generate report.
- Must keep the step order and step logs in `run()` stable, since tests assert on them.

Inputs — `INPUT_*` environment variables, parsed only in `ActionInputs`:

| Input | Env var | Required | Notes |
|---|---|---|---|
| `source-path` | `INPUT_SOURCE_PATH` | yes | deprecated alias `pdf_ready_json` / `INPUT_PDF_READY_JSON` (logs a warning) |
| `output-path` | `INPUT_OUTPUT_PATH` | no | defaults to `output.pdf` |
| `document-type` | `INPUT_DOCUMENT_TYPE` | conditional | one of `user-stories` / `ui-test-catalog` / `coverage-matrix`; `template-path` or `document-type` must be set |
| `template-path` | `INPUT_TEMPLATE_PATH` | conditional | custom Jinja template directory |
| `schema-path` | `INPUT_SCHEMA_PATH` | no | when set, the source JSON is validated before rendering |
| `document-title` | `INPUT_DOCUMENT_TITLE` | no | cover-page title override |
| `debug-html` | `INPUT_DEBUG_HTML` | no | default `false` |
| `verbose` | `INPUT_VERBOSE` | no | default `false`; also true when `RUNNER_DEBUG=1` |

Contract-sensitive outputs:

- Must keep the Action output keys stable — `pdf-path`, `html-path` (only when `debug-html` is set), `report-path` — set via `set_action_output` and exposed by `action.yml` as `pdf_path` / `html_path` / `report_path`.
- Must keep failure strings and exit codes stable — `1` invalid input (`ValueError`), `2` `SchemaValidationError`, `3` `TemplateError`, `4` `RenderingError`, `5` `FileIOError`. Tests assert exact message text.
- Must keep the debug HTML filename pattern `<pdf-stem>_rendered.html`.

## Coding guidelines

- Must keep changes small and scoped to the task.
- Prefer explicit code over clever constructs.
- Must keep externally visible behaviour stable unless the task is an intentional contract change.
- Must not change existing log texts or error messages without a stated reason.
- Prefer pure functions for pipeline logic, and Avoid reading the environment outside `ActionInputs` and `main.run()`.

## Inputs

- Must read every input through `ActionInputs`, and Must not call `os.getenv("INPUT_...")` from any other module.
- Must centralise parsing, defaulting, and validation in `ActionInputs` and `validate_inputs()`.
- Avoid duplicating input validation across modules.
- Must raise `ValueError` for invalid input so `run()` maps it to exit code 1.

## Language and style

- Must target Python 3.10+.
- Must add type hints for new public functions and classes.
- Must keep imports at module top — no imports inside functions or methods.
- Must not disable a linter rule inline unless this file records the exception under Learned rules.

## Logging and string formatting

- Must use `logging`, never `print`.
- Must use lazy `%` formatting in logging calls — `logger.info("msg %s", value)`.
- Must not use f-strings inside logging calls.
- Prefer the clearest formatting when constructing exception and failure messages.

## Docstrings and comments

- Prefer self-explanatory code, and Prefer comments only for intent, edge cases, and the "why".
- Prefer a one-line docstring summary.
- Avoid tutorial-style prose or long examples in docstrings.

## Patterns

- Prefer leaf modules raising the typed exceptions listed under Repo specifics.
- Must let `main.run()` be the only place that translates an exception into GitHub Action failure output and an exit code.
- Prefer private helpers (`_name`) for internal behaviour.
- Must keep integration boundaries — WeasyPrint, the filesystem, the GitHub Actions environment — explicit and mockable.

## Testing

- Must use `pytest` with `pytest-mock`, and Must not use `unittest`.
- Must put unit tests under `tests/unit/` and integration tests under `tests/integration/`.
- Must test behaviour — return values, raised exceptions, log messages, exit codes.
- Must mock `INPUT_*` environment variables in unit tests.
- Must not call external services or run WeasyPrint in unit tests.
- Prefer shared fixtures in `tests/unit/conftest.py` and `tests/integration/conftest.py`.

## Tooling and quality gates

- Must run `make qa` before finishing a code change — it runs `format-check` → `lint` → `types` → `test` and fails on the first failing gate.
- Must use the individual targets while iterating — `make format`, `make format-check`, `make lint`, `make types`, `make test`, `make coverage`.
- Must keep `make lint` (Pylint over tracked `*.py`) at a score of 9.5 or higher.
- Must keep `make format-check` (Black, line length 120, config in `pyproject.toml`) clean.
- Must keep `make types` (mypy, config in `pyproject.toml`) clean, and Prefer fixing types over adding ignores.
- Must keep `make coverage` (pytest, `--cov-fail-under=80`) passing.

## Common pitfalls

- Must verify a new dependency supports Python 3.10 before adding it.
- Must remove unused imports and variables in the same change, and Avoid leaving dead code.
- Avoid changing externally visible strings, output keys, or exit codes unless the task calls for it.
- Must keep `requirements.txt` and `action.yml` in step when inputs or dependencies change.

## Learned rules

- Must keep error messages stable where tests assert exact strings.
- Must not change exit codes for existing failure scenarios.
- Avoid adding inline linter suppressions; the one allowed today is `# pylint: disable=broad-except` on the catch-all handler in `main.run()`.
