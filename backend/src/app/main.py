import logging

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.app.api.routes import auth, cases, documents, organizations, persons, tasks, users
from src.app.api.routes import config as config_routes
from src.app.config import settings
from src.app.db.database import engine, get_db
from src.app.middleware.security import security_middleware
from src.app.models import case, config, document, organization, person, task, user

logger = logging.getLogger(__name__)
load_dotenv()

# Create all tables
user.Base.metadata.create_all(bind=engine)
organization.Base.metadata.create_all(bind=engine)
person.Base.metadata.create_all(bind=engine)
case.Base.metadata.create_all(bind=engine)
document.Base.metadata.create_all(bind=engine)
config.Base.metadata.create_all(bind=engine)
task.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Canada Immigration Operating System",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.middleware("http")(security_middleware)


# Pre-initialize password hashing on startup to avoid first-request errors
@app.on_event("startup")
async def startup_event():
    """Pre-initialize services on startup"""
    try:
        from src.app.services.auth import AuthService

        # Pre-initialize password hashing to avoid first-request errors
        # This ensures bcrypt is ready before first request
        _ = AuthService.get_password_hash("startup_init")
        logger.info("Password hashing pre-initialized successfully")
    except Exception as e:
        # Log but don't fail startup - this is just optimization
        error_msg = str(e)
        # Suppress password-related errors during startup - they don't affect actual usage
        if "72 bytes" in error_msg or "longer than" in error_msg.lower():
            logger.debug(f"Password hashing startup warning (safe to ignore): {error_msg}")
        else:
            logger.warning(
                f"Password hashing pre-initialization warning (non-critical): {error_msg}"
            )


# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Persons"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(config_routes.router, prefix="/api/v1/config", tags=["Configuration"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
from src.app.api.routes import case_evaluation  # noqa: E402

app.include_router(case_evaluation.router, prefix="/api/v1/cases", tags=["Cases"])
# Case evaluation (stateless, config-driven)
from src.app.api.routes import case_evaluation  # noqa: E402

app.include_router(case_evaluation.router, prefix="/api/v1/cases", tags=["Cases"])


@app.get("/")
async def root():
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions"""
    error_msg = str(exc)
    # Handle password-related errors (shouldn't happen with direct bcrypt, but handle gracefully)
    if "72 bytes" in error_msg or "longer than" in error_msg.lower():
        # This error shouldn't occur with direct bcrypt usage, but handle it gracefully
        logger.warning(f"Password processing error (unexpected): {error_msg}")
        return JSONResponse(
            status_code=400,
            content={"detail": "Password processing error. Please try again or contact support."},
        )
    # For other ValueErrors, let route handlers deal with them first
    # If they reach here, return as 400
    logger.warning(f"Unhandled ValueError in {request.url.path}: {error_msg}")
    return JSONResponse(status_code=400, content={"detail": error_msg})


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Simple database connectivity check
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as err:
        raise HTTPException(
            status_code=503, detail=f"Database connection failed: {str(err)}"
        ) from err


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
