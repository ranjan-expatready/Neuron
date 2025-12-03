.PHONY: help install install-dev test test-unit test-integration test-e2e test-coverage lint format type-check clean run dev setup e2e-db-reset e2e-spine test-backend

# Default target
help:
	@echo "FAANG-Level Engineering Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Initial project setup (create venv, install deps)"
	@echo "  make install        - Install production dependencies"
	@echo "  make install-dev    - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-e2e       - Run E2E tests (Playwright)"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Run linters (ruff, isort check)"
	@echo "  make format         - Format code (black, isort)"
	@echo "  make type-check     - Run type checker (mypy)"
	@echo ""
	@echo "Development:"
	@echo "  make run            - Run the API server"
	@echo "  make dev            - Run the API server with auto-reload"
	@echo ""
	@echo "CI Targets:"
	@echo "  make test-backend   - Pytest with coverage gate (mirrors backend-ci workflow)"
	@echo ""
	@echo "E2E Spine:"
	@echo "  make e2e-db-reset   - Reset sqlite e2e.db and seed TestSprite user"
	@echo "  make e2e-spine      - Run TC000 canonical journey (expects servers running)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean build artifacts and cache"

# Variables
PYTHON := python3
VENV := venv
PYTHON_VENV := $(VENV)/bin/python
PIP_VENV := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
BLACK := $(VENV)/bin/black
ISORT := $(VENV)/bin/isort
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy
UVICORN := $(VENV)/bin/uvicorn
TESTSPRITE_UI_BASE_URL ?= http://localhost:3000
E2E_DB := e2e.db
E2E_DB_URL := sqlite:///./$(E2E_DB)

# Setup
setup:
	@echo "Setting up development environment..."
	$(PYTHON) -m venv $(VENV)
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r requirements.txt
	$(PIP_VENV) install -e ".[dev]"
	@echo "✅ Setup complete! Activate with: source $(VENV)/bin/activate"

# Installation
install:
	$(PIP_VENV) install -r requirements.txt

install-dev:
	$(PIP_VENV) install -r requirements.txt
	$(PIP_VENV) install -e ".[dev]"

# Testing
test:
	$(PYTEST) tests/

test-unit:
	$(PYTEST) tests/unit/ -m unit

test-integration:
	$(PYTEST) tests/integration/ -m integration

test-e2e:
	$(PYTEST) tests/e2e/ -m e2e

test-coverage:
	$(PYTEST) --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=80 tests/

test-backend: test-coverage

# Code Quality
lint:
	$(RUFF) check src/ tests/
	$(ISORT) --check-only --diff src/ tests/

format:
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/

type-check:
	$(MYPY) src/

# Development
run:
	$(UVICORN) src.app.main:app --host 0.0.0.0 --port 8000

dev:
	$(UVICORN) src.app.main:app --reload --host 0.0.0.0 --port 8000

e2e-db-reset:
	@echo "🔄 Resetting e2e sqlite database at $(E2E_DB)..."
	rm -f $(E2E_DB)
	PYTHONPATH=src DATABASE_URL=$(E2E_DB_URL) $(PYTHON_VENV) -c "from src.app.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
	PYTHONPATH=src DATABASE_URL=$(E2E_DB_URL) $(PYTHON_VENV) scripts/seed_testsprite_user.py
	@echo "✅ e2e.db ready with TestSprite automation account"

e2e-spine:
	@echo "🏃 Running canonical TC000 spine via Playwright..."
	TESTSPRITE_UI_BASE_URL=$(TESTSPRITE_UI_BASE_URL) $(PYTHON_VENV) ../testsprite_tests/TC000_Full_User_Journey.py
	@echo "✅ TC000 completed"

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/ .coverage
	@echo "✅ Cleaned build artifacts"
