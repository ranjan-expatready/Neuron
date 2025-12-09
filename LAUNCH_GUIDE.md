# 🚀 Launch Guide - Canada Immigration OS

**Quick Start Guide to Launch and View the Application**

---

## 🎯 Quick Start (Recommended - Docker Compose)

### Prerequisites

- Docker & Docker Compose installed
- Ports 3000, 8000, 5432 available

### Step 1: Start Database

```bash
# From project root
docker-compose up -d postgres
```

Wait for database to be ready (~10 seconds)

### Step 2: Start Backend

```bash
cd backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Create .env file (if doesn't exist)
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/canada_immigration_os
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DOCUMENT_STORAGE_PATH=./uploads
EOF

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** http://localhost:8000

### Step 3: Start Frontend

```bash
# Open new terminal, from project root
cd frontend

# Install dependencies (first time only)
npm install

# Create .env.local file (if doesn't exist)
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start frontend server
npm run dev
```

**Frontend will be available at:** http://localhost:3000

---

## 📍 Access Points

### Frontend Application

- **URL:** http://localhost:3000
- **Login Page:** http://localhost:3000/auth/login
- **Register Page:** http://localhost:3000/auth/register
- **Dashboard:** http://localhost:3000/dashboard
- **Cases List:** http://localhost:3000/cases

### Backend API

- **API Base:** http://localhost:8000/api/v1
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🧪 Testing the Application

### 1. Create a User Account

**Via Frontend:**

1. Go to http://localhost:3000/auth/register
2. Fill in registration form
3. Submit to create account

**Via API (using curl):**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Login

**Via Frontend:**

1. Go to http://localhost:3000/auth/login
2. Enter email and password
3. Click "Sign In"

**Via API:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

Save the `access_token` from the response.

### 3. View API Documentation

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Now you can test all endpoints directly in the browser!

### 4. Create a Person

**Via API:**

```bash
curl -X POST http://localhost:8000/api/v1/persons/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  }'
```

### 5. Create a Case

**Via API:**

```bash
# First, get the person_id from previous step
curl -X POST http://localhost:8000/api/v1/cases/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_person_id": "PERSON_ID_FROM_PREVIOUS_STEP",
    "case_type": "EXPRESS_ENTRY_FSW",
    "title": "Express Entry Application",
    "description": "Federal Skilled Worker application"
  }'
```

### 6. View Cases in Frontend

1. Login at http://localhost:3000/auth/login
2. Navigate to http://localhost:3000/cases
3. You should see your cases listed!

---

## 🔧 Manual Setup (Without Docker)

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (or use Docker for just the database)

### Step 1: Database Setup

**Option A: Use Docker for Database Only**

```bash
docker-compose up -d postgres
```

**Option B: Local PostgreSQL**

```bash
# Create database
createdb canada_immigration_os

# Or using psql
psql -U postgres
CREATE DATABASE canada_immigration_os;
\q
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/canada_immigration_os
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DOCUMENT_STORAGE_PATH=./uploads
EOF

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start development server
npm run dev
```

---

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use:**

```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --reload --port 8001
```

**Database connection error:**

- Check PostgreSQL is running: `docker ps` or `pg_isready`
- Verify DATABASE_URL in `.env` matches your database
- Check database exists: `psql -l | grep canada_immigration_os`

**Module not found errors:**

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Issues

**Port 3000 already in use:**

```bash
# Kill process
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

**API connection errors:**

- Check backend is running: http://localhost:8000/health
- Verify NEXT_PUBLIC_API_URL in `.env.local`
- Check CORS settings in backend

**Module not found:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Issues

**Database doesn't exist:**

```bash
# Using Docker
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE canada_immigration_os;"

# Or locally
createdb canada_immigration_os
```

**Tables not created:**

- The app auto-creates tables on startup
- Check backend logs for errors
- Verify database connection in `.env`

---

## 📊 Verify Everything is Working

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy","database":"connected"}`

### 2. Check API Docs

Open http://localhost:8000/docs in browser

- Should see Swagger UI with all endpoints

### 3. Check Frontend

Open http://localhost:3000 in browser

- Should see the application homepage

### 4. Test Full Flow

1. Register user → http://localhost:3000/auth/register
2. Login → http://localhost:3000/auth/login
3. View dashboard → http://localhost:3000/dashboard
4. View cases → http://localhost:3000/cases
5. Create case (via API or UI)
6. Upload document → http://localhost:3000/cases/{id}/upload

---

## 🎯 Quick Test Script

Save this as `quick-test.sh`:

```bash
#!/bin/bash

echo "🧪 Testing Canada Immigration OS..."

# Test backend health
echo "1. Testing backend health..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Backend is healthy" || echo "❌ Backend not responding"

# Test API docs
echo "2. Testing API docs..."
curl -s http://localhost:8000/docs | grep -q "Swagger" && echo "✅ API docs accessible" || echo "❌ API docs not accessible"

# Test frontend
echo "3. Testing frontend..."
curl -s http://localhost:3000 | grep -q "html" && echo "✅ Frontend is running" || echo "❌ Frontend not responding"

echo "✅ All checks complete!"
```

Run: `chmod +x quick-test.sh && ./quick-test.sh`

---

## 📝 Environment Variables Reference

### Backend (.env)

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/canada_immigration_os
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DOCUMENT_STORAGE_PATH=./uploads
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🎉 Success!

Once everything is running:

- ✅ Backend: http://localhost:8000/docs
- ✅ Frontend: http://localhost:3000
- ✅ Database: Running on port 5432

**You're ready to explore the application!**

---

## 📚 Next Steps

1. **Explore API:** Visit http://localhost:8000/docs
2. **Create Account:** Register at http://localhost:3000/auth/register
3. **Create Cases:** Use the API or UI to create test cases
4. **Upload Documents:** Test document upload with OCR processing
5. **View Statistics:** Check case statistics endpoint

---

**Need Help?** Check the logs:

- Backend: Terminal running `uvicorn`
- Frontend: Terminal running `npm run dev`
- Database: `docker-compose logs postgres`
