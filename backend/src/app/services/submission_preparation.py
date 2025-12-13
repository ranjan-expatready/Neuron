from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.app.services.form_autofill_engine import FormAutofillEngine, FormAutofillEngineError
from src.app.services.submission_readiness_verification import (
    EvidenceBundle,
    SubmissionReadinessVerificationService,
)


PREPARATION_ENGINE_VERSION = "1.0.0"


class PreparationField(BaseModel):
    field_code: str
    source: str
    value_preview: Optional[object]
    status: str
    notes: Optional[str] = None


class PreparationAttachment(BaseModel):
    doc_code: str
    status: str
    evidence_ref: Optional[str] = None


class PreparationForm(BaseModel):
    form_code: str
    form_name: Optional[str] = None
    fields: List[PreparationField]
    attachments: List[PreparationAttachment]


class GapsSummary(BaseModel):
    blocking: List[str]
    non_blocking: List[str]


class SubmissionPreparationPackage(BaseModel):
    package_version: str = "v1"
    case_id: str
    tenant_id: str
    program_code: str
    engine_versions: List[str]
    evaluation_timestamp: str
    forms: List[PreparationForm]
    gaps_summary: GapsSummary
    readiness_reference: dict
    audit: dict
    deterministic_hash: str


class SubmissionPreparationServiceError(Exception):
    """Base error for submission preparation."""


class SubmissionPreparationService:
    def __init__(
        self,
        *,
        base_path: Optional[str] = None,
        readiness_service: Optional[SubmissionReadinessVerificationService] = None,
        form_engine: Optional[FormAutofillEngine] = None,
    ) -> None:
        self._base_path = base_path
        self._readiness_service = readiness_service or SubmissionReadinessVerificationService(base_path=base_path)
        self._form_engine = form_engine or FormAutofillEngine(base_path=base_path)

    def _hash_package(self, payload: dict) -> str:
        # Exclude deterministic_hash itself to avoid recursion
        payload_no_hash = {k: v for k, v in payload.items() if k != "deterministic_hash"}
        data = json.dumps(payload_no_hash, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def _status_for_field(self, value: object) -> str:
        return "missing" if value is None else "mapped"

    def _attachments_from_readiness(self, evidence: EvidenceBundle) -> List[PreparationAttachment]:
        readiness = evidence.readiness_result
        attachments: List[PreparationAttachment] = []
        missing = set(readiness.missing_documents or [])
        for doc in readiness.documents or []:
            status = "missing" if doc.id in missing else "available"
            evidence_ref = doc.config_ref or doc.source_ref
            attachments.append(
                PreparationAttachment(
                    doc_code=doc.id,
                    status=status,
                    evidence_ref=evidence_ref,
                )
            )
        # Ensure deterministic order
        return sorted(attachments, key=lambda a: a.doc_code)

    def build_package(
        self,
        *,
        case_id: str,
        tenant_id: str,
        program_code: Optional[str],
        db_session: Session,
    ) -> SubmissionPreparationPackage:
        try:
            evidence = self._readiness_service.build_evidence_bundle(
                case_id=case_id,
                tenant_id=tenant_id,
                program_code=program_code,
                db_session=db_session,
            )
        except Exception as exc:  # pragma: no cover
            raise SubmissionPreparationServiceError(str(exc)) from exc

        readiness = evidence.readiness_result
        program = program_code or evidence.program_code

        try:
            preview = self._form_engine.build_autofill_preview(
                case_id=case_id,
                program_code=program,
                tenant_id=tenant_id,
                db_session=db_session,
            )
        except FormAutofillEngineError as exc:
            raise SubmissionPreparationServiceError(str(exc)) from exc

        attachments = self._attachments_from_readiness(evidence)

        forms: List[PreparationForm] = []
        blocking_gaps: List[str] = []
        non_blocking_gaps: List[str] = []

        for form in sorted(preview.forms, key=lambda f: f.form_id):
            prep_fields: List[PreparationField] = []
            for field in sorted(form.fields, key=lambda f: f.field_id):
                status = self._status_for_field(field.proposed_value)
                if status == "missing":
                    blocking_gaps.append(f"field:{form.form_id}:{field.field_id}")
                prep_fields.append(
                    PreparationField(
                        field_code=field.field_id,
                        source=field.source_type,
                        value_preview=field.proposed_value,
                        status=status,
                        notes=field.notes,
                    )
                )

            prep_attachments = attachments
            for att in prep_attachments:
                if att.status == "missing":
                    blocking_gaps.append(f"attachment:{form.form_id}:{att.doc_code}")

            forms.append(
                PreparationForm(
                    form_code=form.form_id,
                    form_name=None,
                    fields=prep_fields,
                    attachments=prep_attachments,
                )
            )

        eval_ts = evidence.evaluation_timestamp or readiness.evaluation_timestamp or datetime.now(timezone.utc).isoformat()

        package = SubmissionPreparationPackage(
            case_id=case_id,
            tenant_id=tenant_id,
            program_code=program,
            engine_versions=[
                f"prep:{PREPARATION_ENGINE_VERSION}",
                f"readiness:{readiness.engine_version or 'unknown'}",
                f"verification:{evidence.verification_engine_version}",
            ],
            evaluation_timestamp=eval_ts,
            forms=forms,
            gaps_summary=GapsSummary(
                blocking=sorted(set(blocking_gaps)),
                non_blocking=sorted(set(non_blocking_gaps)),
            ),
            readiness_reference={
                "readiness_verdict": evidence.verification_result.verdict,
                "evidence_bundle_ref": evidence.config_hashes[0] if getattr(evidence, "config_hashes", None) else None,
            },
            audit={
                "config_hashes": getattr(evidence, "config_hashes", []) or [],
                "consulted_configs": getattr(evidence, "consulted_configs", []) or [],
                "source_bundle_version": getattr(evidence, "source_bundle_version", None),
            },
            deterministic_hash="",
        )

        package.deterministic_hash = self._hash_package(package.model_dump())
        return package

