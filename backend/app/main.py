from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from dotenv import load_dotenv

from .db.database import engine, get_db
from .models import user, organization, person, case, config
from .api.routes import auth, users, organizations, persons, cases, config as config_routes

load_dotenv()

# Create all tables
user.Base.metadata.create_all(bind=engine)
organization.Base.metadata.create_all(bind=engine)
person.Base.metadata.create_all(bind=engine)
case.Base.metadata.create_all(bind=engine)
config.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Canada Immigration OS API",
    description="Backend API for Canada Immigration Operating System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
origins = [
    "http://localhost:3000",  # Next.js frontend
    "http://localhost:3001",
    "https://localhost:3000",
    "https://localhost:3001",
]

# Add environment-specific origins
if os.getenv("FRONTEND_URL"):
    origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Persons"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(config_routes.router, prefix="/api/v1/config", tags=["Configuration"])

@app.get("/")
async def root():
    return {"message": "Canada Immigration OS API", "version": "1.0.0"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Simple database connectivity check
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)