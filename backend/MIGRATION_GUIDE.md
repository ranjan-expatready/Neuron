# Migration Guide: Old Structure → New Structure

**Date:** December 3, 2025

---

## 🔄 What Changed

### Structure Migration

- **Old:** `backend/app/` → **New:** `backend/src/app/`
- **Old:** `backend/tests/` (flat) → **New:** `backend/tests/unit/`, `tests/integration/`, `tests/e2e/`

### Import Changes

- **Old:** `from app.module import X`
- **New:** `from src.app.module import X`

---

## 📋 Migration Steps

### 1. Update Entry Points

**Files Updated:**

- ✅ `backend/src/app/main.py` - Updated imports
- ✅ `backend/start_backend.sh` - Updated uvicorn command
- ✅ `backend/run_tests.py` - Updated coverage path

### 2. Update Test Files

**Automated:**

- ✅ All test files updated to use `src.app.*` imports
- ✅ Tests moved to `unit/` and `integration/` directories

**Manual Check Needed:**

- Verify all tests still pass
- Update any hardcoded paths

### 3. Update CI/CD

**Files Updated:**

- ✅ `.github/workflows/backend-ci.yml` - Updated paths to `src`

### 4. Update Configuration

**Files Updated:**

- ✅ `backend/pytest.ini` - Updated coverage path
- ✅ `backend/pyproject.toml` - New file with tool configs

---

## 🔍 Verification

### Check Imports

```bash
# Find any remaining old imports
cd backend
grep -r "from app\." src/ tests/ || echo "✅ No old imports found"
grep -r "import app\." src/ tests/ || echo "✅ No old imports found"
```

### Run Tests

```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
make test
```

### Check Server

```bash
# Start server
make dev

# Test health endpoint
curl http://localhost:8000/health
```

---

## ⚠️ Known Issues

1. **Relative Imports in src/app:**

   - Files within `src/app/` still use relative imports (e.g., `from ..models`)
   - This is fine and works correctly
   - Only entry points and tests use absolute imports

2. **Database Migrations:**
   - Alembic may need path updates if it references models
   - Check `alembic/env.py` if migrations fail

---

## ✅ Migration Complete

All major files have been updated. The new structure is ready for use!

---

**Next:** Run `make test` to verify everything works! 🚀
