# Contributing

## Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/docs/#installation)
- Git

---

## Local setup

```bash
git clone https://github.com/mimickerhq/mimicker.git
cd mimicker

make install          # install runtime + dev dependencies
make pre-commit-install  # install git hooks (do this once)
```

That's it — the pre-commit hooks run automatically on every `git commit`.

---

## Running tests

```bash
make test             # full suite with coverage
make test-fast        # fast run, stops on first failure
make test LOGS=1      # full suite with live Mimicker logs
```

Open the coverage report after a run:

```bash
make test-cov
```

---

## Pre-commit hooks

Every commit is checked automatically:

| Hook | What it does |
|---|---|
| `trailing-whitespace` | Strips trailing spaces |
| `end-of-file-fixer` | Ensures files end with a newline |
| `check-yaml` | Validates YAML syntax |
| `check-added-large-files` | Blocks accidentally large files |
| `lint` | Syntax-checks every changed `.py` file |
| `tests` | Runs the full test suite — commit is blocked if tests fail |

To run all hooks manually against every file:

```bash
make pre-commit-run
```

!!! tip "First time slow"
    The first `pre-commit-run` downloads hook environments — subsequent runs are instant.

---

## Docs

```bash
make install-docs     # install mkdocs-material
make docs-serve       # live preview at http://127.0.0.1:8000/mimicker/
make docs-build       # build to site/ (strict — warnings are errors)
```

---

## All available commands

```bash
make help
```

---

## Submitting a pull request

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Ensure `make test` and `make pre-commit-run` both pass
4. Open a PR against `main` — CI will run the full test suite

---

## Community

- [Slack](https://join.slack.com/t/mimicker/shared_invite/zt-2yr7vubw4-8Y09YyxZ5j~G2tlQ5uOXKw)
- [Issues](https://github.com/mimickerhq/mimicker/issues)
