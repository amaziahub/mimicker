.PHONY: all

test:
	@echo "Running tests..."
	poetry run pytest --cov=mimicker --cov-report=xml --cov-report=html


install:
	@echo "Installing dependencies..."
	poetry install

activate:
	@echo "activate poetry env"
	poetry shell
