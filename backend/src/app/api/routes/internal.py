from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.app.db.database import get_db
from src.app.observability.metrics import metrics_registry

router = APIRouter()


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail="database not ready") from exc
    return {"status": "ready"}


@router.get("/metrics")
async def metrics():
    return metrics_registry.snapshot()
