from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import List, Tuple

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.app.services.submission_readiness import (
    ENGINE_VERSION,
    SubmissionReadinessEngine,
    SubmissionReadinessEngineError,
    SubmissionReadinessResult,
)


class VerificationVerdict(str):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class VerificationResult(BaseModel):
    verdict: str
    reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class EvidenceBundle(BaseModel):
    bundle_version: str = "v1"
    case_id: str
    tenant_id: str
    program_code: str
    engine_version: str
    verification_engine_version: str = "1.0.0"
    evaluation_timestamp: str
    config_hashes: List[str]
    consulted_configs: List[str]
    source_bundle_version: str
    readiness_result: SubmissionReadinessResult
    verification_result: VerificationResult
    evidence_index: List[str]


class SubmissionReadinessVerificationService:
    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = base_path
        self.engine = SubmissionReadinessEngine(base_path=base_path)

    def _config_files(self) -> List[str]:
        return [p.name for p in sorted(self.engine._config_files(), key=lambda p: p.name)]  # type: ignore[attr-defined]

    def _config_hashes(self, readiness: SubmissionReadinessResult, evidence_index: List[str]) -> List[str]:
        refs_hash = hashlib.sha256("".join(evidence_index).encode("utf-8")).hexdigest()
        return sorted({readiness.config_hash, refs_hash})

    def _collect_evidence_refs(
        self, readiness: SubmissionReadinessResult
    ) -> Tuple[List[str], List[str]]:
        config_refs: List[str] = []
        source_refs: List[str] = []
        for doc in readiness.documents:
            if doc.config_ref:
                config_refs.append(doc.config_ref)
            if doc.source_ref:
                source_refs.append(doc.source_ref)
        for blk in readiness.blockers:
            config_refs.extend(blk.config_refs or [])
            source_refs.extend(blk.source_refs or [])
        return sorted(set(config_refs)), sorted(set(source_refs))

    def _verify(self, readiness: SubmissionReadinessResult) -> VerificationResult:
        reasons: List[str] = []
        warnings: List[str] = []

        for blk in readiness.blockers:
            if not blk.config_refs:
                reasons.append(f"blocker_missing_config_ref:{blk.code}")
            if not blk.source_refs:
                reasons.append(f"blocker_missing_source_ref:{blk.code}")

        for doc in readiness.documents:
            if doc.unsourced and doc.required:
                reasons.append(f"unsourced_requirement:{doc.id}")
            if doc.required and doc.unsourced and doc.uploaded:
                warnings.append(f"unsourced_uploaded:{doc.id}")

        if readiness.status.upper() == "UNKNOWN":
            reasons.append("status_unknown")

        verdict = VerificationVerdict.PASS
        if "status_unknown" in reasons:
            verdict = VerificationVerdict.UNKNOWN
        elif reasons:
            verdict = VerificationVerdict.FAIL

        if readiness.missing_documents != sorted(readiness.missing_documents):
            warnings.append("missing_documents_not_sorted")
        if readiness.blockers != sorted(readiness.blockers, key=lambda b: b.code):
            warnings.append("blockers_not_sorted")
        if readiness.documents != sorted(
            readiness.documents, key=lambda d: (d.id, d.category)
        ):
            warnings.append("documents_not_sorted")

        return VerificationResult(
            verdict=verdict,
            reasons=sorted(set(reasons)),
            warnings=sorted(set(warnings)),
        )

    def _build_unknown_readiness(
        self, case_id: str, tenant_id: str, program_code: str | None, reason: str
    ) -> SubmissionReadinessResult:
        timestamp = datetime.now(timezone.utc).isoformat()
        return SubmissionReadinessResult(
            case_id=case_id,
            tenant_id=tenant_id,
            program_code=program_code or "UNKNOWN",
            status="UNKNOWN",
            ready=False,
            missing_documents=[],
            documents=[],
            blockers=[],
            explanations=[reason],
            engine_version=ENGINE_VERSION,
            evaluation_timestamp=timestamp,
            config_hash=self.engine._config_hash(),  # type: ignore[attr-defined]
            source_bundle_version="unknown",
        )

    def build_evidence_bundle(
        self,
        *,
        case_id: str,
        tenant_id: str,
        program_code: str | None = None,
        db_session: Session,
    ) -> EvidenceBundle:
        try:
            readiness = self.engine.evaluate_case(
                case_id=case_id,
                program_code=program_code,
                tenant_id=tenant_id,
                db_session=db_session,
            )
        except SubmissionReadinessEngineError as exc:
            msg = str(exc)
            if "ambiguous" in msg.lower():
                readiness = self._build_unknown_readiness(case_id, tenant_id, program_code, msg)
            else:
                raise

        verification = self._verify(readiness)
        config_refs, source_refs = self._collect_evidence_refs(readiness)
        evidence_index = sorted(set(config_refs + source_refs))

        bundle = EvidenceBundle(
            case_id=readiness.case_id,
            tenant_id=readiness.tenant_id,
            program_code=readiness.program_code,
            engine_version=readiness.engine_version,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
            config_hashes=self._config_hashes(readiness, evidence_index),
            consulted_configs=self._config_files(),
            source_bundle_version=readiness.source_bundle_version,
            readiness_result=readiness,
            verification_result=verification,
            evidence_index=evidence_index,
        )
        return bundle


__all__ = [
    "SubmissionReadinessVerificationService",
    "EvidenceBundle",
    "VerificationResult",
    "VerificationVerdict",
]

