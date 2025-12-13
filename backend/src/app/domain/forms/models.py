from __future__ import annotations

from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class FormFieldAutofill(BaseModel):
    form_id: str
    field_id: str
    proposed_value: Optional[Any]
    source_type: Literal["canonical_profile", "document", "rule_engine", "constant"]
    source_path: Optional[str] = None
    notes: Optional[str] = None
    conflicts: List[str] = Field(default_factory=list)


class FormAutofillResult(BaseModel):
    form_id: str
    fields: List[FormFieldAutofill] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class FormAutofillPreviewResult(BaseModel):
    bundle_id: Optional[str] = None
    forms: List[FormAutofillResult] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# Phase 12.1 Submission Preparation Models

class FieldPrepResult(BaseModel):
    field_code: str
    field_name: str
    resolved_value: Optional[Any] = None
    source: Literal["canonical_profile", "autofill_mapping", "not_resolved"]
    status: Literal["resolved", "unresolved"]
    reason: Optional[str] = None


class FormPrepResult(BaseModel):
    form_code: str
    form_name: str
    fields: List[FieldPrepResult] = Field(default_factory=list)
    attachment_required: bool = False
    status: Literal["resolved", "partial", "unresolved"]


class AttachmentPlan(BaseModel):
    document_type: str
    required_for_form: str
    attached_document_ids: List[str] = Field(default_factory=list)
    status: Literal["attached", "missing"]
    reason: Optional[str] = None


class ReadinessGap(BaseModel):
    """Represents a gap in submission readiness."""
    gap_type: Literal["missing_document", "unresolved_field", "incomplete_form"]
    description: str
    severity: Literal["blocking", "warning"] = "blocking"
    related_form: Optional[str] = None
    related_field: Optional[str] = None


class SubmissionPrepResult(BaseModel):
    case_id: str
    program_code: Optional[str] = None
    form_bundle_id: Optional[str] = None
    forms: List[FormPrepResult] = Field(default_factory=list)
    document_attachments: List[AttachmentPlan] = Field(default_factory=list)
    blocking_gaps: List[ReadinessGap] = Field(default_factory=list)
    summary_ready: bool
    generated_at: datetime
    reasons: List[str] = Field(default_factory=list)

