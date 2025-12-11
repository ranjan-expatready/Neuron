from __future__ import annotations

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

