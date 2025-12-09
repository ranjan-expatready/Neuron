from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

from src.app.domain_config.service import ConfigService
from src.app.rules.models import CandidateProfile


class DocumentItem(BaseModel):
    id: str
    label: str
    category: str
    mandatory: bool = True


class DocumentMatrixResult(BaseModel):
    required_forms: list[str] = Field(default_factory=list)
    required_documents: list[DocumentItem] = Field(default_factory=list)


class ProgramDocuments(BaseModel):
    base: list[DocumentItem] = Field(default_factory=list)
    spouse: list[DocumentItem] = Field(default_factory=list)
    pof_required: list[DocumentItem] = Field(default_factory=list)


class DocumentsConfig(BaseModel):
    documents: Dict[str, ProgramDocuments] = Field(default_factory=dict)


class FormsConfig(BaseModel):
    forms: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class DocumentConfigBundle:
    documents: DocumentsConfig
    forms: FormsConfig


class DocumentMatrixService:
    """
    Config-driven document + forms resolver.
    Uses ConfigService for domain rules (e.g., PoF exemptions) and local YAML for documents/forms.
    """

    def __init__(self, config_service: ConfigService, base_path: Optional[Path] = None) -> None:
        self.config_service = config_service
        # repo root = parents[4]; align with DomainRulesConfigService
        self.base_path = base_path or Path(__file__).resolve().parents[4] / "config" / "domain"
        self._bundle: Optional[DocumentConfigBundle] = None

    def _load_yaml(self, name: str) -> Dict[str, Any]:
        path = self.base_path / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Missing config file: {path}")
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load_bundle(self) -> DocumentConfigBundle:
        if self._bundle:
            return self._bundle
        docs_raw = self._load_yaml("documents")
        forms_raw = self._load_yaml("forms")
        docs_cfg = DocumentsConfig(
            documents={
                code: ProgramDocuments(**program_docs)
                for code, program_docs in docs_raw.get("documents", {}).items()
            }
        )
        forms_cfg = FormsConfig(forms=forms_raw.get("forms", {}))
        self._bundle = DocumentConfigBundle(documents=docs_cfg, forms=forms_cfg)
        return self._bundle

    def get_bundle(self) -> DocumentConfigBundle:
        """Expose the cached documents/forms bundle for read-only callers."""
        return self._load_bundle()

    def get_required_documents(self, profile: CandidateProfile, program: str) -> DocumentMatrixResult:
        bundle = self._load_bundle()
        domain_cfg = self.config_service.get_domain_rules()
        program_docs = bundle.documents.documents.get(program.lower(), ProgramDocuments())
        req_docs: list[DocumentItem] = []

        # Base docs
        req_docs.extend(program_docs.base)

        # Spouse docs (simple heuristic on marital_status)
        if profile.marital_status and profile.marital_status.lower() in ("married", "common-law"):
            req_docs.extend(program_docs.spouse)

        # PoF docs
        uses_pof = False
        for pr in domain_cfg.program_rules.programs:
            if pr.code.lower() == program.lower():
                uses_pof = pr.uses_proof_of_funds
                break
        if uses_pof and program not in domain_cfg.proof_of_funds.exemptions:
            req_docs.extend(program_docs.pof_required)

        # Forms
        required_forms: list[str] = []
        express_entry_forms = bundle.forms.forms.get("express_entry", {})
        if isinstance(express_entry_forms, dict):
            required_forms.extend(express_entry_forms.get(program.lower(), []))
        spouse_forms = bundle.forms.forms.get("spouse", [])
        if profile.marital_status and profile.marital_status.lower() in ("married", "common-law"):
            if isinstance(spouse_forms, list):
                required_forms.extend(spouse_forms)

        return DocumentMatrixResult(
            required_forms=required_forms,
            required_documents=req_docs,
        )

