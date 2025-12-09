# 🚀 Setup and Visual Testing Guide

## Current Status

**Issue Detected:** Services need to be started before visual testing.

### Prerequisites Check

1. **Docker** - Not running (needed for PostgreSQL)

   - Start Docker Desktop or install Docker
   - Alternative: Use local PostgreSQL or SQLite for testing

2. **Backend Dependencies** - May need installation

   - Python 3.11+ required
   - Some dependencies may need system libraries (psycopg2)

3. **Frontend Dependencies** - May need installation
   - Node.js 18+ required
   - npm packages need installation

---

## Quick Setup Options

### Option 1: Use SQLite (Easiest - No Docker Needed)

**Backend Setup:**

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (may need to skip psycopg2 for SQLite)
pip install fastapi uvicorn sqlalchemy python-jose passlib bcrypt python-multipart pydantic python-dotenv

# Create .env with SQLite
cat > .env << EOF
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DOCUMENT_STORAGE_PATH=./uploads
EOF

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup:**

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

### Option 2: Use Docker (Recommended)

**Start Docker Desktop first, then:**

```bash
# Start database
docker-compose up -d postgres

# Wait for database to be ready
sleep 5

# Start backend (in one terminal)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev
```

---

## Visual Testing Checklist

Once services are running:

### 1. Health Check

- [ ] Backend: http://localhost:8000/health
- [ ] Frontend: http://localhost:3000

### 2. API Documentation

- [ ] Visit: http://localhost:8000/docs
- [ ] Should see Swagger UI with all endpoints

### 3. Frontend Pages

- [ ] Homepage: http://localhost:3000
- [ ] Login: http://localhost:3000/auth/login
- [ ] Register: http://localhost:3000/auth/register
- [ ] Dashboard: http://localhost:3000/dashboard (after login)
- [ ] Cases: http://localhost:3000/cases (after login)

### 4. Functional Testing

- [ ] Register new user
- [ ] Login with credentials
- [ ] View dashboard
- [ ] Create a person
- [ ] Create a case
- [ ] Upload a document
- [ ] View case details

---

## Current Blockers

1. **Docker not running** - PostgreSQL can't start

   - Solution: Start Docker Desktop or use SQLite

2. **Backend dependencies** - psycopg2 build issues

   - Solution: Use SQLite or install PostgreSQL dev libraries

3. **Services not started** - Need to start backend and frontend
   - Solution: Follow setup steps above

---

## Next Steps

1. **Choose setup option** (SQLite or Docker)
2. **Start services** (backend and frontend)
3. **Verify health** (check /health endpoints)
4. **Visual testing** (browser navigation and interaction)

Would you like me to:

- A) Help set up with SQLite (no Docker needed)?
- B) Wait for you to start Docker and then test?
- C) Create a simplified test setup script?

---

**Note:** Once services are running, I can navigate the browser and visually test all features for you!
