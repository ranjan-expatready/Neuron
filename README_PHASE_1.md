# Canada Immigration OS - Phase 1 Development Setup

This document explains how to set up and run the Phase 1 implementation of Canada Immigration OS locally.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose (optional, for containerized development)

## Project Structure

```
├── backend/           # FastAPI backend service
│   ├── app/          # Application code
│   │   ├── api/      # API routes and endpoints
│   │   ├── models/   # SQLAlchemy database models
│   │   ├── schemas/  # Pydantic schemas for API
│   │   ├── services/ # Business logic services
│   │   ├── db/       # Database configuration and migrations
│   │   └── main.py   # FastAPI application entry point
│   └── tests/        # Backend tests
├── frontend/         # Next.js frontend application
│   ├── app/          # Next.js app router pages
│   ├── components/   # React components
│   ├── lib/          # Utility functions and configurations
│   ├── types/        # TypeScript type definitions
│   └── tests/        # Frontend tests
├── docs/             # Project documentation
│   ├── AI_CORE/      # AI Core and Meta-Engines specification (Thread A)
│   ├── architecture/ # System architecture documentation
│   ├── product/      # Product requirements and specifications
│   └── *.md          # Master specifications and phase documentation
├── infra/            # Infrastructure and deployment configs
├── .github/workflows/ # CI/CD workflows
└── README_PHASE_1.md # This file
```

## Quick Start

### 1. Database Setup

#### Option A: Using Docker Compose (Recommended)
```bash
cd infra
docker-compose up -d postgres
```

#### Option B: Local PostgreSQL
```bash
# Create database
createdb canada_immigration_os_dev
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your backend URL

# Start the development server
npm run dev
```

The frontend will be available at: http://localhost:3000

## Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## API Endpoints (Phase 1)

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh JWT token

### Organizations
- `GET /orgs/current` - Get current user's organization
- `PUT /orgs/current` - Update organization details

### Persons
- `GET /persons` - List persons (org-scoped)
- `POST /persons` - Create new person
- `GET /persons/{id}` - Get person details
- `PUT /persons/{id}` - Update person
- `DELETE /persons/{id}` - Delete person

### Cases
- `GET /cases` - List cases (org-scoped)
- `POST /cases` - Create new case
- `GET /cases/{id}` - Get case details
- `PUT /cases/{id}` - Update case
- `DELETE /cases/{id}` - Delete case

### Configuration (Read-only in Phase 1)
- `GET /config/case-types` - List available case types
- `GET /config/forms` - Get form configurations
- `GET /config/fields` - Get field configurations

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/canada_immigration_os_dev
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Workflow

1. Make changes to backend or frontend code
2. Tests run automatically on file changes (if using watch mode)
3. Commit changes following conventional commit format
4. Push to trigger CI/CD pipeline

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in backend/.env
- Verify database exists and user has permissions

### CORS Issues
- Ensure frontend URL is in backend CORS origins
- Check NEXT_PUBLIC_API_URL in frontend/.env.local

### Port Conflicts
- Backend runs on port 8000
- Frontend runs on port 3000
- PostgreSQL runs on port 5432
- Modify ports in respective config files if needed

## Phase 1 Status

✅ **COMPLETED:**
- [x] Monorepo structure setup
- [x] Backend core services (FastAPI + SQLAlchemy)
- [x] Database models and schemas (User, Organization, Person, Case, Configuration)
- [x] Complete API routes with authentication
- [x] Alembic migrations setup
- [x] Frontend skeleton (Next.js + TypeScript + Tailwind CSS)
- [x] Authentication pages (login/register)
- [x] Dashboard implementation
- [x] GitHub Actions CI/CD workflows
- [x] Docker Compose setup for local development
- [x] Development setup scripts

🎉 **PHASE 1 COMPLETE!**

The foundation is now ready for Phase 2 development.

## Next Steps (Phase 2+)

- Implement AI agent orchestration
- Add document processing capabilities
- Implement eligibility assessment engine
- Add client portal features
- Integrate with external APIs (IRCC, payment processors)