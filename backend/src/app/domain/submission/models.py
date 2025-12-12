from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ReadinessSeverity(str, Enum):
    INFO = "info"
    WARN = "warn"
    BLOCKER = "blocker"


class ReadinessCheckResult(BaseModel):
    code: str
    severity: ReadinessSeverity
    message: str
    field_id: Optional[str] = None
    data_path: Optional[str] = None
    document_code: Optional[str] = None
    form_id: Optional[str] = None
    suggested_fix: Optional[str] = None
    evidence: Dict[str, Any] = Field(
        default_factory=dict,
        description="Keys/paths only, no PII or raw text extracts.",
    )


class FormReadinessSummary(BaseModel):
    form_id: str
    title: str
    completion_percent: int = Field(..., ge=0, le=100)
    missing_required_fields: int
    missing_required_documents: int
    checks: List[ReadinessCheckResult] = Field(default_factory=list)


class SubmissionReadinessReport(BaseModel):
    case_id: str
    bundle_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    overall_status: Literal["READY", "NEEDS_REVIEW", "NOT_READY"]
    overall_completion_percent: int = Field(..., ge=0, le=100)
    blockers_count: int
    warnings_count: int
    forms: List[FormReadinessSummary] = Field(default_factory=list)
    missing_documents: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

