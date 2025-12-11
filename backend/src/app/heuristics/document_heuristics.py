from __future__ import annotations

import datetime
import re
from typing import Any, Dict, List, Optional

from src.app.models.document import Document

HeuristicFinding = Dict[str, Any]


class DocumentHeuristicsEngine:
    """
    Deterministic, rule-based heuristics for document content/metadata.
    No ML/LLM. Shadow-only findings.
    """

    REQUIRED_KEYWORDS = {
        "passport_main": ["surname", "given name", "passport"],
        "ielts_trf": ["candidate", "test report", "trf", "centre"],
    }

    FORBIDDEN_HINTS = {
        "proof_of_funds": ["birth", "certificate"],
    }

    def __init__(self) -> None:
        self.now_year = datetime.datetime.utcnow().year

    @staticmethod
    def _has_keywords(text: str, keywords: List[str]) -> List[str]:
        lowered = text.lower()
        return [kw for kw in keywords if kw.lower() not in lowered]

    @staticmethod
    def _extract_years_from_filename(filename: Optional[str]) -> List[int]:
        if not filename:
            return []
        return [int(y) for y in re.findall(r"(19|20)\d{2}", filename)]

    @staticmethod
    def _canonical_name(profile: Optional[dict]) -> Optional[str]:
        if not isinstance(profile, dict):
            return None
        base = profile.get("profile", profile)
        if not isinstance(base, dict):
            return None
        personal = base.get("personal") or {}
        if not isinstance(personal, dict):
            personal = {}
        first = personal.get("given_name") or personal.get("first_name")
        last = personal.get("family_name") or personal.get("last_name")
        if first and last:
            return f"{first} {last}"
        if personal.get("client_name"):
            return personal.get("client_name")
        return None

    def analyze(
        self,
        *,
        doc_definition: Any,
        uploaded_doc: Document,
        ocr_text: Optional[str],
        canonical_profile: dict,
    ) -> List[HeuristicFinding]:
        findings: List[HeuristicFinding] = []
        text = ocr_text or ""
        doc_id = getattr(uploaded_doc, "id", None)
        requirement_id = getattr(doc_definition, "id", None)
        doc_type = getattr(uploaded_doc, "document_type", None)
        filename = getattr(uploaded_doc, "filename", None)
        mime_type = getattr(uploaded_doc, "mime_type", None)
        file_size = getattr(uploaded_doc, "file_size", None)

        # 1) Missing semantic content
        if text:
            missing = self._has_keywords(
                text, self.REQUIRED_KEYWORDS.get(requirement_id or doc_type, [])
            )
            if missing:
                findings.append(
                    {
                        "document_id": doc_id,
                        "document_type": doc_type,
                        "requirement_id": requirement_id,
                        "finding_code": f"{requirement_id or doc_type}.missing_keywords",
                        "severity": "warning",
                        "details": {"missing_keywords": missing},
                    }
                )

        # 2) Wrong/misplaced documents (heuristic via forbidden hints)
        forbidden = self.FORBIDDEN_HINTS.get(requirement_id or doc_type)
        if forbidden and text:
            present = [kw for kw in forbidden if kw.lower() in text.lower()]
            if present:
                findings.append(
                    {
                        "document_id": doc_id,
                        "document_type": doc_type,
                        "requirement_id": requirement_id,
                        "finding_code": f"{requirement_id or doc_type}.suspect_misplaced",
                        "severity": "warning",
                        "details": {"found_hints": present},
                    }
                )

        # 3) Expired documents (filename year heuristic)
        years = self._extract_years_from_filename(filename)
        if years:
            most_recent = max(years)
            if most_recent < self.now_year - 2:
                findings.append(
                    {
                        "document_id": doc_id,
                        "document_type": doc_type,
                        "requirement_id": requirement_id,
                        "finding_code": f"{requirement_id or doc_type}.possibly_expired",
                        "severity": "info",
                        "details": {"most_recent_year_in_filename": most_recent},
                    }
                )

        # 4) Quality warnings: very low char density or tiny file size, non-PDF passport
        if text and len(text.strip()) < 50:
            findings.append(
                {
                    "document_id": doc_id,
                    "document_type": doc_type,
                    "requirement_id": requirement_id,
                    "finding_code": f"{requirement_id or doc_type}.low_character_density",
                    "severity": "warning",
                    "details": {"length": len(text.strip())},
                }
            )
        if file_size is not None and file_size < 5 * 1024:
            findings.append(
                {
                    "document_id": doc_id,
                    "document_type": doc_type,
                    "requirement_id": requirement_id,
                    "finding_code": f"{requirement_id or doc_type}.small_file",
                    "severity": "warning",
                    "details": {"file_size_bytes": file_size},
                }
            )
        if requirement_id and requirement_id.startswith("passport") and mime_type:
            if not mime_type.startswith("application/pdf") and not mime_type.startswith("image/"):
                findings.append(
                    {
                        "document_id": doc_id,
                        "document_type": doc_type,
                        "requirement_id": requirement_id,
                        "finding_code": "passport.unexpected_mime_type",
                        "severity": "warning",
                        "details": {"mime_type": mime_type},
                    }
                )

        # 5) Cross-field consistency: name presence
        canonical_name = self._canonical_name(canonical_profile)
        if canonical_name and text:
            if canonical_name.lower() not in text.lower():
                findings.append(
                    {
                        "document_id": doc_id,
                        "document_type": doc_type,
                        "requirement_id": requirement_id,
                        "finding_code": f"{requirement_id or doc_type}.name_mismatch",
                        "severity": "warning",
                        "details": {"expected_name": canonical_name},
                    }
                )

        return findings


__all__ = ["DocumentHeuristicsEngine", "HeuristicFinding"]


