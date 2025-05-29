.PHONY: setup lint test build clean all help

help:
	@echo "Available commands:"
	@echo "  make lint    - Run code quality checks"
	@echo "  make test    - Run tests with coverage"
	@echo "  make build   - Build package distributions"
	@echo "  make clean   - Remove build artifacts"
	@echo "  make all     - Run full CI workflow"

# Install all dependencies
setup:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info .coverage htmlcov/

# Run linting checks
lint:
	black --check --verbose src/ tests/
	isort --check --diff src/ tests/
	pylint src/ tests/

# Run tests with coverage
test:
	pytest --cov=wiley_tdm --cov-report=xml --cov-report=html

# Build package
build:
	python -m build
	twine check dist/*

# Run all checks
all: setup clean lint test build
