.PHONY: test test-unit test-live test-coverage lint typecheck format install install-dev clean bootstrap verify pr meta

# Default target
.DEFAULT_GOAL := test

# Bootstrap and PR workflow
bootstrap:
	@bash scripts/bootstrap.sh

verify: lint format-check typecheck test
	@echo "✅ All quality gates passed"

pr:
	@bash scripts/pr.sh

meta:
	@bash scripts/repo_meta.sh

# Install
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

# Testing
test:
	pytest -m "not live"

test-unit:
	pytest tests/unit

test-protocol:
	pytest tests/protocol/test_tier1_deterministic.py

test-live:
	@echo "Running live smoke tests (requires ETHYS_MODE=live)"
	ETHYS_MODE=live pytest -m live

test-coverage:
	pytest --cov=ethys402_crewai --cov-report=term-missing --cov-report=html -m "not live"

test-all:
	pytest

# Code quality
lint:
	ruff check ethys402_crewai/ tests/ examples/

typecheck:
	mypy ethys402_crewai/

format:
	black ethys402_crewai/ tests/ examples/

format-check:
	black --check ethys402_crewai/ tests/ examples/

# Cleanup
clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/ .mypy_cache

