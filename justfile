set dotenv-load := true
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

export PYTHONUTF8 := "1"

default: lint

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

# execute test cases
test *args:
    uv run pytest --cov ulid_django {{ args }}

# execute test cases against a specific Python version
test-py version *args:
    uv run --python {{ version }} pytest --cov ulid_django {{ args }}

# execute test cases against every supported Python version
test-all *args: (test-py "3.12" args) (test-py "3.13" args) (test-py "3.14" args)

# build the source distribution and wheel
build:
    uv build --clear
