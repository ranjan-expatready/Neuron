import json
import logging
from typing import Any, Dict, Optional


def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)
    return logger


def _clean_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}
    for key, value in fields.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            cleaned[key] = value
        else:
            cleaned[key] = str(value)
    return cleaned


def log_structured(
    logger: logging.Logger,
    level: int,
    message: str,
    *,
    request_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    component: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> None:
    payload: Dict[str, Any] = {
        "message": message,
        "request_id": request_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "path": path,
        "method": method,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "component": component,
        "log_level": logging.getLevelName(level),
    }
    if extra_fields:
        payload.update(extra_fields)
    logger.log(level, json.dumps(_clean_fields(payload)))


def log_info(
    *,
    logger: logging.Logger,
    message: str,
    request=None,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    component: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> None:
    log_structured(
        logger,
        logging.INFO,
        message,
        request_id=getattr(request.state, "request_id", None) if request else None,
        tenant_id=tenant_id,
        user_id=user_id,
        path=str(request.url.path) if request else None,
        method=request.method if request else None,
        status_code=status_code,
        duration_ms=duration_ms,
        component=component,
        extra_fields=extra_fields,
    )


def log_error(
    *,
    logger: logging.Logger,
    message: str,
    request=None,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    component: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> None:
    log_structured(
        logger,
        logging.ERROR,
        message,
        request_id=getattr(request.state, "request_id", None) if request else None,
        tenant_id=tenant_id,
        user_id=user_id,
        path=str(request.url.path) if request else None,
        method=request.method if request else None,
        status_code=status_code,
        duration_ms=duration_ms,
        component=component,
        extra_fields=extra_fields,
    )
