.PHONY: install install-docs activate \
        test test-fast test-cov \
        lint format \
        pre-commit-install pre-commit-run \
        docs-serve docs-build docs-clean \
        docker-build docker-run docker-stop \
        validate-stubs \
        clean help

# ── Dependencies ──────────────────────────────────────────────────────────────

install:
	@echo "Installing dependencies..."
	poetry install

install-docs:
	@echo "Installing docs dependencies..."
	poetry install --with docs

activate:
	@echo "Activating poetry env..."
	poetry shell

# ── Testing ───────────────────────────────────────────────────────────────────

LOGS ?= 0

ifeq ($(LOGS),1)
  _LOG_ENV   = MIMICKER_LOG_LEVEL=DEBUG
  _LOG_FLAGS = -s --log-cli-level=DEBUG --log-cli-format="%(message)s"
else
  _LOG_ENV   =
  _LOG_FLAGS =
endif

test:
	@echo "Running tests..."
	$(_LOG_ENV) poetry run pytest --cov=mimicker --cov-report=xml --cov-report=html $(_LOG_FLAGS)

test-fast:
	@echo "Running tests (no coverage)..."
	$(_LOG_ENV) poetry run pytest -x -q $(_LOG_FLAGS)

test-cov:
	@echo "Opening coverage report..."
	open htmlcov/index.html

# ── Code quality ──────────────────────────────────────────────────────────────

lint:
	@echo "Linting..."
	poetry run python -m py_compile mimicker/*.py && echo "OK"

format:
	@echo "Formatting..."
	poetry run python -m black mimicker/ tests/ 2>/dev/null || echo "black not installed — run: pip install black"

# ── Pre-commit ────────────────────────────────────────────────────────────────

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	poetry run pre-commit install

pre-commit-run:
	@echo "Running pre-commit on all files..."
	poetry run pre-commit run --all-files

# ── Docs ──────────────────────────────────────────────────────────────────────

docs-serve:
	@echo "Serving docs at http://127.0.0.1:8000/mimicker/ ..."
	poetry run mkdocs serve

docs-build:
	@echo "Building docs..."
	poetry run mkdocs build --strict

docs-clean:
	@echo "Cleaning docs build..."
	rm -rf site/

# ── Docker ────────────────────────────────────────────────────────────────────

DOCKER_IMAGE ?= mimicker-local
MIMICKER_PORT ?= 8080

docker-build:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE) .

docker-run:
	@echo "Running Mimicker on port $(MIMICKER_PORT)..."
	docker run --rm -p $(MIMICKER_PORT):$(MIMICKER_PORT) \
		-e MIMICKER_PORT=$(MIMICKER_PORT) \
		$(DOCKER_IMAGE)

docker-stop:
	@echo "Stopping Mimicker containers..."
	docker ps -q --filter ancestor=$(DOCKER_IMAGE) | xargs -r docker stop

# ── CLI helpers ───────────────────────────────────────────────────────────────

validate-stubs: ## Validate a stubs file: make validate-stubs FILE=stubs.yaml
	@test -n "$(FILE)" || (echo "Usage: make validate-stubs FILE=<path>"; exit 1)
	poetry run mimicker validate $(FILE)

# ── Housekeeping ──────────────────────────────────────────────────────────────

clean:
	@echo "Cleaning build artifacts..."
	rm -rf site/ htmlcov/ coverage.xml .coverage dist/ __pycache__ mimicker/__pycache__ tests/__pycache__

help:
	@printf "\n"
	@printf "\033[1;96m  Mimicker — Developer Makefile\033[0m\n"
	@printf "\033[90m  ─────────────────────────────────────────────\033[0m\n"
	@printf "\n"
	@printf "\033[1;34m  Dependencies\033[0m\n"
	@printf "  \033[96minstall\033[0m           Install runtime + dev dependencies\n"
	@printf "  \033[96minstall-docs\033[0m      Install docs dependencies (mkdocs-material)\n"
	@printf "  \033[96mactivate\033[0m          Activate poetry shell\n"
	@printf "\n"
	@printf "\033[1;34m  Testing\033[0m\n"
	@printf "  \033[96mtest\033[0m              Run full test suite with coverage\n"
	@printf "  \033[96mtest-fast\033[0m         Run tests without coverage (stops on first fail)\n"
	@printf "  \033[96mtest-cov\033[0m          Open HTML coverage report in browser\n"
	@printf "  \033[90m↳ append LOGS=1 to any test target for live Mimicker logs\033[0m\n"
	@printf "\n"
	@printf "\033[1;34m  Code Quality\033[0m\n"
	@printf "  \033[96mlint\033[0m              Syntax-check all source files\n"
	@printf "  \033[96mformat\033[0m            Auto-format with black\n"
	@printf "  \033[96mpre-commit-install\033[0m  Install pre-commit hooks into .git\n"
	@printf "  \033[96mpre-commit-run\033[0m    Run all pre-commit hooks on every file\n"
	@printf "\n"
	@printf "\033[1;34m  Docs\033[0m\n"
	@printf "  \033[96mdocs-serve\033[0m        Live-preview docs at localhost:8000\n"
	@printf "  \033[96mdocs-build\033[0m        Build docs to site/ (strict)\n"
	@printf "  \033[96mdocs-clean\033[0m        Remove site/ build directory\n"
	@printf "\n"
	@printf "\033[1;34m  Docker\033[0m\n"
	@printf "  \033[96mdocker-build\033[0m      Build Docker image  \033[90m(DOCKER_IMAGE=mimicker-local)\033[0m\n"
	@printf "  \033[96mdocker-run\033[0m        Run Docker image    \033[90m(MIMICKER_PORT=8080)\033[0m\n"
	@printf "  \033[96mdocker-stop\033[0m       Stop running Mimicker containers\n"
	@printf "\n"
	@printf "\033[1;34m  CLI Helpers\033[0m\n"
	@printf "  \033[96mvalidate-stubs\033[0m    Validate a YAML stubs file  \033[90m(FILE=<path>)\033[0m\n"
	@printf "\n"
	@printf "\033[1;34m  Housekeeping\033[0m\n"
	@printf "  \033[96mclean\033[0m             Remove all build artifacts\n"
	@printf "\n"
	@printf "\033[90m  Usage: make <target>   e.g. make test-fast\033[0m\n"
	@printf "\n"
