import logging
import time
import uuid

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.app.api.routes import (
    admin_config,
    auth,
    billing_admin,
    cases,
    documents,
    intake,
    organizations,
    persons,
    tasks,
    users,
)
from src.app.api.routes import config as config_routes
from src.app.api.routes.internal import router as internal_router

from src.app.config import settings
from src.app.cases import models_db as case_history_models
from src.app.db.database import engine, get_db
from src.app.middleware.security import security_middleware
from src.app.models import case, config, document, organization, person, task, user, billing
from src.app.observability.logging import get_logger, log_info, log_error
from src.app.observability.metrics import metrics_registry
from src.app.security.errors import (
    ForbiddenError,
    LifecyclePermissionError,
    PlanLimitError,
    TenantAccessError,
    UnauthorizedError,
    SecurityError,
)

logger = get_logger(__name__)
load_dotenv()

# Create all tables
user.Base.metadata.create_all(bind=engine)
organization.Base.metadata.create_all(bind=engine)
person.Base.metadata.create_all(bind=engine)
case.Base.metadata.create_all(bind=engine)
document.Base.metadata.create_all(bind=engine)
config.Base.metadata.create_all(bind=engine)
task.Base.metadata.create_all(bind=engine)
case_history_models.Base.metadata.create_all(bind=engine)

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

# Observability middleware (request_id, timing, metrics, structured log)
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        duration_ms = (time.perf_counter() - start) * 1000
        metrics_registry.record_request(request.method, request.url.path, status_code, duration_ms)
        log_error(
            logger=logger,
            message="request.failed",
            request=request,
            status_code=status_code,
            duration_ms=duration_ms,
            component="http_request",
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    metrics_registry.record_request(request.method, request.url.path, status_code, duration_ms)
    log_info(
        logger=logger,
        message="request.completed",
        request=request,
        status_code=status_code,
        duration_ms=duration_ms,
        component="http_request",
    )
    response.headers["X-Request-ID"] = request_id
    return response

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
app.include_router(intake.router, prefix="/api/v1", tags=["Intake"])
app.include_router(config_routes.router, prefix="/api/v1/config", tags=["Configuration"])
app.include_router(admin_config.router, prefix="/api/v1/admin/config", tags=["Admin Configuration"])
app.include_router(billing_admin.router, prefix="/api/v1/admin/billing", tags=["Billing Admin"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
from src.app.api.routes import case_evaluation, case_history, case_lifecycle  # noqa: E402

app.include_router(case_evaluation.router, prefix="/api/v1/cases", tags=["Cases"])
from src.app.api.routes import case_profile  # noqa: E402

app.include_router(case_profile.router, prefix="/api/v1", tags=["Cases"])
app.include_router(internal_router, prefix="/internal", tags=["Internal"])
app.include_router(
    case_history.router,
    prefix="/api/v1/case-history",
    tags=["Case History"],
)
app.include_router(
    case_lifecycle.router,
    prefix="/api/v1",
    tags=["Case Lifecycle"],
)


@app.get("/")
async def root():
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(
        status_code=exc.status_code,
        content=SecurityError(error="unauthorized", detail=exc.detail, status_code=exc.status_code).model_dump(),
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(
        status_code=exc.status_code,
        content=SecurityError(error="forbidden", detail=exc.detail, status_code=exc.status_code).model_dump(),
    )


@app.exception_handler(TenantAccessError)
async def tenant_handler(request: Request, exc: TenantAccessError):
    return JSONResponse(
        status_code=exc.status_code,
        content=SecurityError(error="tenant_access", detail=exc.detail, status_code=exc.status_code).model_dump(),
    )


@app.exception_handler(LifecyclePermissionError)
async def lifecycle_handler(request: Request, exc: LifecyclePermissionError):
    return JSONResponse(
        status_code=exc.status_code,
        content=SecurityError(
            error="lifecycle_permission", detail=exc.detail, status_code=exc.status_code
        ).model_dump(),
    )


@app.exception_handler(PlanLimitError)
async def plan_limit_handler(request: Request, exc: PlanLimitError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "plan_limit_exceeded", "detail": exc.detail, "status_code": exc.status_code},
    )


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
