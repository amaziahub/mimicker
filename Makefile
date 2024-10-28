.PHONY: all

test:
	@echo "Running tests..."
	pytest

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
