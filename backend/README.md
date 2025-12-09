# Canada Immigration OS - Backend

FAANG-level production-grade backend for Canada Immigration OS.

## 🏗️ Project Structure

```
backend/
├── src/
│   └── app/              # Application code
│       ├── api/          # API routes and endpoints
│       ├── config.py     # Centralized configuration
│       ├── db/           # Database configuration
│       ├── main.py       # FastAPI application entry point
│       ├── middleware/  # Middleware (security, etc.)
│       ├── models/       # SQLAlchemy database models
│       ├── schemas/      # Pydantic schemas
│       ├── services/     # Business logic services
│       ├── utils/        # Utility functions
│       └── agents/       # Agentic workflows (future)
├── tests/
│   ├── unit/            # Unit tests (fast, isolated)
│   ├── integration/     # Integration tests
│   ├── e2e/             # End-to-end tests (Playwright)
│   └── conftest.py      # Pytest fixtures
├── alembic/             # Database migrations
├── pyproject.toml       # Modern Python project config
├── requirements.txt     # Dependencies
├── Makefile            # Automation commands
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Virtual environment (venv)

### Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install-dev
# OR
pip install -r requirements.txt
pip install -e ".[dev]"

# Install Playwright browsers (for E2E tests)
playwright install
```

### Backend Runtime (Python 3.10)

- Required version: **Python 3.10.x** (repo verified with 3.10.19; see `.python-version`).
- Recommended workflow:
  1. `cd backend`
  2. `rm -rf .venv && python3.10 -m venv .venv`
  3. `source .venv/bin/activate`
  4. `python -m pip install --upgrade pip`
  5. `pip install -r requirements.txt`
- Canonical test commands:
  - `cd backend && source .venv/bin/activate && pytest`
  - `cd backend && source .venv/bin/activate && pytest -m "unit"`
  - `cd backend && source .venv/bin/activate && pytest -m "integration"`
  - `cd backend && source .venv/bin/activate && pytest --cov=src`

### Run the Server

```bash
# Using Makefile
make dev

# OR directly
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# OR using the startup script
./start_backend.sh
```

### Run Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# E2E tests (Playwright)
make test-e2e

# With coverage report
make test-coverage
```

### Backend Testing Spine

- Tests live in `tests/unit` (fast, isolated logic) and `tests/integration` (API + DB flows).
- Canonical commands:
  - `cd backend && pytest`
  - `cd backend && pytest -m "unit"`
  - `cd backend && pytest -m "integration"`
- Coverage target stays at **80%+**; every backend feature must land with unit and/or integration specs wired into this spine before review.

## 🧪 Testing

### Test Structure

- **Unit Tests** (`tests/unit/`): Fast, isolated tests with no external dependencies
- **Integration Tests** (`tests/integration/`): Tests that verify component interactions
- **E2E Tests** (`tests/e2e/`): Full system tests using Playwright

### Running Specific Tests

```bash
# Run specific test file
pytest tests/unit/test_auth.py

# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m e2e

# Run with coverage
pytest --cov=src --cov-report=html
```

### Test Coverage

Target: **80%+ coverage**

```bash
make test-coverage
# Open htmlcov/index.html to view coverage report
```

## 🔧 Code Quality

### Formatting

```bash
# Format code
make format

# Check formatting (CI)
make lint
```

### Type Checking

```bash
make type-check
```

## 📦 Dependencies

### Production

- FastAPI - Web framework
- SQLAlchemy - ORM
- Alembic - Database migrations
- Pydantic - Data validation
- Python-JOSE - JWT tokens
- bcrypt - Password hashing

### Development

- pytest - Testing framework
- pytest-cov - Coverage reporting
- pytest-playwright - E2E testing
- black - Code formatting
- isort - Import sorting
- ruff - Linting
- mypy - Type checking

## 🏭 CI/CD

GitHub Actions workflows:

- `.github/workflows/backend-ci.yml` - Continuous integration
- Runs tests, linting, and coverage checks on every PR

## 🔐 Configuration

Configuration is managed through:

- Environment variables (`.env` file)
- `src/app/config.py` - Centralized settings using Pydantic Settings

Key environment variables:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret key
- `FRONTEND_URL` - Frontend URL for CORS
- `ENVIRONMENT` - Environment (development/production/testing)

## 📚 API Documentation

Once the server is running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤖 Agentic Workflows

Future support for:

- CrewAI agents
- LangGraph workflows
- Multi-agent orchestration

Structure: `src/app/agents/`

## 🎯 FAANG-Level Practices

This project follows FAANG-level engineering practices:

- ✅ **Tests First**: Tests written alongside or before code
- ✅ **Type Hints**: Full type annotation
- ✅ **Code Quality**: Automated linting and formatting
- ✅ **Coverage**: 80%+ test coverage requirement
- ✅ **CI/CD**: Automated testing and deployment
- ✅ **Documentation**: Clear structure and README
- ✅ **Configuration**: Centralized config management

## 📝 Development Workflow

1. **Create feature branch**
2. **Write tests first** (TDD)
3. **Implement feature**
4. **Run tests**: `make test`
5. **Format code**: `make format`
6. **Check quality**: `make lint`
7. **Commit**: Pre-commit hooks run automatically
8. **Create PR**: CI runs automatically

## 🆘 Troubleshooting

### Import Errors

If you see import errors, ensure:

- Virtual environment is activated
- Dependencies are installed: `make install-dev`
- Python path includes `backend/` directory

### Test Failures

- Check database connection (tests use SQLite in-memory)
- Ensure all dependencies are installed
- Run `make clean` to clear caches

### Playwright Issues

```bash
# Reinstall Playwright browsers
playwright install
```

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Python](https://playwright.dev/python/)

---

**Built with FAANG-level engineering standards** 🚀
