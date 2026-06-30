# Living Doc Generator PDF—for Developers

- [Get Started](#get-started)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Run Static Code Analysis](#running-static-code-analysis)
- [Run Black Tool Locally](#run-black-tool-locally)
- [Run mypy Tool Locally](#run-mypy-tool-locally)
- [Running Unit Test](#running-unit-test)
- [Running Integration Tests](#running-integration-tests)
- [Code Coverage](#code-coverage)
- [Interpreting Test Failures](#interpreting-test-failures)
- [Run Action Locally](#run-action-locally)
- [Branch Naming Convention](#branch-naming-convention)

## Get Started

Clone the repository and navigate to the project directory:

```shell
git clone https://github.com/AbsaOSS/living-doc-generator-pdf.git
cd living-doc-generator-pdf
```

Install the dependencies:

```shell
pip install -r requirements.txt
```

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to enforce code quality and consistency before commits. Pre-commit automatically runs formatting, linting, and type checking on your code.

### Install Pre-commit

After installing project dependencies, set up pre-commit hooks:

```shell
pip install pre-commit
pre-commit install
```

This configures Git to run pre-commit hooks before each commit.

### Using Pre-commit

Pre-commit runs automatically on staged files when you commit:

```shell
git add <files>
git commit -m "Your commit message"
```

If any hook fails, the commit will be blocked, and you'll see which checks failed. Fix the issues and try committing again.

### Manual Pre-commit Runs

Run pre-commit on all files manually:

```shell
pre-commit run --all-files
```

Run pre-commit on specific files:

```shell
pre-commit run --files <file1> <file2>
```

### Update Pre-commit Hooks

Keep hooks up to date:

```shell
pre-commit autoupdate
```

### Pre-commit Hooks in This Project

The `.pre-commit-config.yaml` configuration includes:
- **Black**: Code formatting (line length 120, target Python 3.14)
- **Pylint**: Static code analysis (score threshold ≥ 9.5)
- **mypy**: Type checking
- **General hooks**: Trailing whitespace, end-of-file fixer, YAML syntax, etc.

### Skip Pre-commit (Not Recommended)

In rare cases, you can skip pre-commit hooks:

```shell
git commit --no-verify -m "Your commit message"
```

Note: CI will still run all checks, so skipping pre-commit locally may result in CI failures.

## Running Static Code Analysis

This project uses the Pylint tool for static code analysis. Pylint analyzes your code without actually running it. It checks for errors, enforces coding standards, looks for code smells, etc.

Pylint displays a global evaluation score for the code, rated out of a maximum score of 10.0. We aim to keep our code quality above 9.5.

### Set Up Python Environment
```shell
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

This command will also install a Pylint tool, since it is listed in the project requirements.

### Run Pylint
Run Pylint on all files currently tracked by Git in the project.
```shell
pylint $(git ls-files '*.py')
```

To run Pylint on a specific file, follow the pattern `pylint <path_to_file>/<name_of_file>.py`.

Example:
```shell
pylint generator/action_inputs.py
```

## Run Black Tool Locally
This project uses the [Black](https://github.com/psf/black) tool for code formatting.
Black aims for consistency, generality, readability, and reducing git diffs.
The coding style used can be viewed as a strict subset of PEP 8.

The project root file `pyproject.toml` defines the Black tool configuration.
In this project, we are accepting a line length of 120 characters.

Follow these steps to format your code with Black locally:

### Set Up Python Environment
From the terminal in the root of the project, run the following command:

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This command will also install a Black tool, since it is listed in the project requirements.

### Run Black
Run Black on all files currently tracked by Git in the project.
```shell
black $(git ls-files '*.py')
```

To run Black on a specific file, follow the pattern `black <path_to_file>/<name_of_file>.py`.

Example:
```shell
black generator/action_inputs.py
```

### Expected Output
This is the console's expected output example after running the tool:
```
All done! ✨ 🍰 ✨
1 file reformatted.
```

## Run mypy Tool Locally

This project uses the [my[py]](https://mypy.readthedocs.io/en/stable/) tool, a static type checker for Python.

> Type checkers help ensure that you correctly use variables and functions in your code.
> With mypy, add type hints (PEP 484) to your Python programs,
> and mypy will warn you when you use those types incorrectly.
my[py] configuration is in `pyproject.toml` file.

Follow these steps to format your code with my[py] locally:

### Run my[py]

Run my[py] on all files in the project.
```shell
  mypy .
```

To run my[py] check on a specific file, follow the pattern `mypy <path_to_file>/<name_of_file>.py --check-untyped-defs`.

Example:
```shell
mypy generator/action_inputs.py --check-untyped-defs
```

## Running Unit Test

Unit tests are written using pytest. To run the tests, use the following command:

```shell
pytest tests/unit
```

This will execute all tests located in the tests/unit directory.

## Running Integration Tests

Integration tests verify end-to-end functionality of the PDF generator using real file I/O and actual PDF generation. These tests are located in `tests/integration/` and cover:

- **PDF Generation**: End-to-end scenarios for all three built-in document types (`user-stories`, `ui-test-catalog`, `coverage-matrix`) plus a minimal empty-items case
- **Custom Templates**: Full override, partial override (fallback to built-in), and custom CSS scenarios
- **Error Handling**: Error scenarios with expected exit codes (missing file, schema violation, template syntax, read-only directory)
- **Edge Cases**: Empty items, minimal fields, large markdown content, special characters and Unicode
- **Debug HTML**: HTML rendering and filename-pattern scenarios

### Run All Integration Tests

```shell
export PYTHONPATH=$(pwd)
pytest tests/integration/ -v
```

### Run Specific Integration Test Files

```shell
# Test PDF generation scenarios
pytest tests/integration/test_pdf_generation.py -v

# Test custom template behavior
pytest tests/integration/test_custom_templates.py -v

# Test error handling and exit codes
pytest tests/integration/test_error_handling.py -v

# Test edge cases
pytest tests/integration/test_edge_cases.py -v

# Test debug HTML output
pytest tests/integration/test_debug_html.py -v
```

### Run Specific Test

```shell
pytest tests/integration/test_pdf_generation.py::test_generate_pdf_minimal -v
```

### Integration Test Artifacts

Integration tests generate PDFs in temporary directories (cleaned up automatically). To inspect generated PDFs during development:

1. Run tests with `--tb=short` to see detailed output
2. Check temporary directories printed in test output
3. Use `pytest -s` to see print statements

## Code Coverage

Code coverage is collected using the pytest-cov coverage tool. To run the tests and collect coverage information, use the following command:

```shell
pytest --cov=. -v tests/unit --cov-fail-under=80                      # Check coverage threshold
pytest --cov=. -v tests/unit --cov-fail-under=80 --cov-report=html    # Generate HTML report
```

This will execute all tests in the tests directory and generate a code coverage report.

See the coverage report on the path:

```shell
open htmlcov/index.html
```

### Understanding Coverage Reports

The HTML coverage report shows:

- **Green lines**: Covered by tests
- **Red lines**: Not covered by tests
- **Yellow lines**: Partially covered (e.g., branches)
- **Overall percentage**: Total code coverage

**Coverage targets:**
- Overall: ≥ 80%
- Critical modules (schema_validator, action_inputs): ≥ 90%

### Coverage for Specific Modules

```shell
# Check coverage for a specific module
pytest --cov=generator.schema_validator tests/unit/generator/test_schema_validator.py --cov-report=term-missing

# Check coverage for all generator modules
pytest --cov=generator --cov=main tests/unit/ --cov-report=term-missing
```

## Interpreting Test Failures

### Unit Test Failures

Unit tests typically fail due to:

1. **Logic errors**: Fix the implementation in `generator/` modules
2. **API changes**: Update tests to match new interfaces
3. **Mock/fixture issues**: Update test fixtures in `tests/unit/conftest.py`

Example failure:
```
FAILED tests/unit/generator/test_schema_validator.py::test_validate_missing_schema_version
AssertionError: Expected SchemaValidationError with message matching 'schema_version'
```

**Action**: Check the error message format in `generator/schema_validator.py` and update the test assertion or fix the code.

### Integration Test Failures

Integration tests typically fail due to:

1. **File I/O errors**: Check file permissions, disk space
2. **PDF generation errors**: Check WeasyPrint dependencies (fonts, etc.)
3. **Schema validation errors**: Update test JSON to match schema requirements
4. **Template errors**: Fix template syntax or update templates

Example failure:
```
FAILED tests/integration/test_pdf_generation.py::test_generate_pdf_minimal
generator.schema_validator.SchemaValidationError: Missing required field 'tags'
```

**Action**: Update the test JSON data to include all required schema fields.

### CI/CD Failures

When tests fail in CI but pass locally:

1. **Environment differences**: Check Python version (CI uses 3.14)
2. **Missing dependencies**: Verify `requirements.txt` includes all dependencies
3. **Path issues**: Ensure `PYTHONPATH` is set correctly in CI workflow
4. **Artifact generation**: Check if CI has permission to write files

View CI logs in GitHub Actions for detailed stack traces and error messages.

## Run Action Locally
A ready-made `run_locally.sh` script is included in the project root. Edit the `INPUT_*` variables at the top to match your source file and document type, then run:

```bash
bash run_locally.sh
```

The key variables to configure:

```bash
export INPUT_SOURCE_PATH="examples/user_stories.json"   # path to your source JSON
export INPUT_DOCUMENT_TYPE="user-stories"                # user-stories | ui-test-catalog | coverage-matrix
export INPUT_OUTPUT_PATH="output.pdf"
export INPUT_DEBUG_HTML="true"
export INPUT_VERBOSE="true"
# Optional:
# export INPUT_TEMPLATE_PATH="./custom_templates"        # custom template directory
# export INPUT_SCHEMA_PATH="generator/schemas/doc-issues-v1.0.0-schema.json"
```

### macOS Prerequisites

WeasyPrint depends on system-level libraries that are not bundled with the Python package.
Install them via [Homebrew](https://brew.sh/) before running the script:

```shell
brew install pango gdk-pixbuf libffi
```

Without these libraries, the script will fail with:
```
OSError: cannot load library 'libgobject-2.0-0'
```

The `run_locally.sh` script sets `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` so the dynamic linker can find the Homebrew-installed libraries. If you run tests directly, prepend the variable:

```shell
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib python3 -m pytest tests/
```

## Branch Naming Convention
All work branches MUST use an allowed prefix followed by a concise kebab-case descriptor (optional numeric ID):
Allowed prefixes:
- feature/ : new functionality & enhancements
- fix/     : bug fixes / defect resolutions
- docs/    : documentation-only updates
- chore/   : maintenance, CI, dependency bumps, non-behavioral refactors
Examples:
- feature/add-hierarchy-support
- fix/456-null-title-parsing
- docs/update-readme-quickstart
- chore/upgrade-pygithub
Rules:
- Prefix mandatory; rename non-compliant branches before PR (`git branch -m feature/<new-name>` etc.).
- Descriptor lowercase kebab-case; hyphens only; avoid vague terms (`update`, `changes`).
- Align scope: a docs-only PR MUST use docs/ prefix, not feature/.
Verification Tip:
```shell
git rev-parse --abbrev-ref HEAD | grep -E '^(feature|fix|docs|chore)/' || echo 'Branch naming violation (expected allowed prefix)'
```
Future possible prefixes (not enforced yet): `refactor/`, `perf/`.
