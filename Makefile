# ============================================================================
# RED-SHADOW v4.0 - Ambani Integration Makefile
# ============================================================================
# Quick commands for dependency management and common tasks
# ============================================================================

.PHONY: help install install-dev install-minimal verify clean test lint format

# Default target
help:
	@echo "RED-SHADOW v4.0 - Ambani Integration"
	@echo "===================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make install         - Install all dependencies"
	@echo "  make install-dev     - Install development dependencies"
	@echo "  make install-minimal - Install minimal dependencies"
	@echo "  make verify          - Verify installation"
	@echo "  make clean           - Clean Python cache files"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linters"
	@echo "  make format          - Format code"
	@echo "  make docs            - Build documentation"
	@echo "  make update          - Update dependencies"
	@echo ""

# Install all dependencies
install:
	@echo "Installing all dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✓ Installation complete"

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	pip install --upgrade pip
	pip install -r requirements-dev.txt
	@echo "✓ Development installation complete"

# Install minimal dependencies
install-minimal:
	@echo "Installing minimal dependencies..."
	python setup_dependencies.py --mode minimal
	@echo "✓ Minimal installation complete"

# Verify installation
verify:
	@echo "Verifying installation..."
	python setup_dependencies.py --verify

# Clean Python cache files
clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "✓ Cleanup complete"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=ambani_integration --cov-report=html --cov-report=term

# Run linters
lint:
	@echo "Running linters..."
	flake8 ambani_integration/ tests/
	pylint ambani_integration/
	mypy ambani_integration/
	bandit -r ambani_integration/

# Format code
format:
	@echo "Formatting code..."
	black ambani_integration/ tests/
	isort ambani_integration/ tests/
	@echo "✓ Code formatted"

# Build documentation
docs:
	@echo "Building documentation..."
	cd docs && make html
	@echo "✓ Documentation built (see docs/_build/html/index.html)"

# Update dependencies
update:
	@echo "Updating dependencies..."
	pip install --upgrade -r requirements.txt
	@echo "✓ Dependencies updated"

# Check for security vulnerabilities
security:
	@echo "Checking for security vulnerabilities..."
	safety check -r requirements.txt
	bandit -r ambani_integration/

# Generate requirements with hashes
freeze:
	@echo "Generating requirements with versions..."
	pip freeze > requirements-frozen.txt
	@echo "✓ Frozen requirements saved to requirements-frozen.txt"

# Setup pre-commit hooks
setup-hooks:
	@echo "Setting up pre-commit hooks..."
	pre-commit install
	@echo "✓ Pre-commit hooks installed"

# Run all checks (lint + test + security)
check: lint test security
	@echo "✓ All checks passed"
