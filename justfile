set dotenv-load

[windows]
set shell := ["powershell.exe", "-NoLogo", "-Command"]

export PYTHONUTF8 := "1"

default: ruff

# set up development environment
dev-setup:
    uv sync
    uv run pre-commit install

# run ruff linter and formatter
ruff:
    uv run ruff check --fix .
    uv run ruff format .

# execute all linters
lint:
    uv run pre-commit run --all-files

# audit locked dependencies for known vulnerabilities
audit:
    uv audit --frozen

# execute test cases
test *args:
    uv run pytest --cov ulid_django {{ args }}

# execute test cases against a specific Python version
test-py version *args:
    uv run --python {{ version }} pytest --cov ulid_django {{ args }}

# execute test cases against a specific Django feature release
test-django version *args:
    uv run --frozen --with 'django=={{ version }}.*' pytest --cov ulid_django {{ args }}

# execute test cases against every supported Python and Django version
test-all *args: (test-py "3.12" args) (test-py "3.13" args) (test-py "3.14" args) (test-django "5.2" args) (test-django "6.0" args)

# build the source distribution and wheel
build:
    uv build --clear

# The PyPI token lives in Windows Credential Manager; WSL has no Secret Service
# backend. uv only consults the keyring when an explicit username is supplied.
# build and publish the distribution to PyPI
[confirm("Publish to PyPI? This cannot be undone. [y/N]")]
[windows]
publish: build
    uv publish --username __token__ --keyring-provider subprocess
