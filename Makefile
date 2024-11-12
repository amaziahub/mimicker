.PHONY: all

test:
	@echo "Running tests..."
	poetry run pytest


install:
	@echo "Installing dependencies..."
	poetry install
