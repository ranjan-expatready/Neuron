from __future__ import annotations

from fastapi import status
from pydantic import BaseModel


class SecurityError(BaseModel):
    error: str
    detail: str
    status_code: int


class UnauthorizedError(Exception):
    def __init__(self, detail: str = "Unauthorized") -> None:
        self.detail = detail
        self.status_code = status.HTTP_401_UNAUTHORIZED
        super().__init__(detail)


class ForbiddenError(Exception):
    def __init__(self, detail: str = "Forbidden") -> None:
        self.detail = detail
        self.status_code = status.HTTP_403_FORBIDDEN
        super().__init__(detail)


class TenantAccessError(ForbiddenError):
    def __init__(self, detail: str = "Access denied for tenant") -> None:
        super().__init__(detail)


class LifecyclePermissionError(ForbiddenError):
    def __init__(self, detail: str = "Lifecycle action not permitted for role") -> None:
        super().__init__(detail)


class PlanLimitError(ForbiddenError):
    def __init__(self, detail: str = "Plan limit exceeded") -> None:
        super().__init__(detail)

