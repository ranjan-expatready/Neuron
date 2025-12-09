from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel

from src.app.domain_config.service import ConfigService, DomainConfigBundle
from src.app.documents.service import (
    DocumentConfigBundle,
    DocumentMatrixService,
    DocumentsConfig,
    FormsConfig,
)
from src.app.rules.config_models import (
    ArrangedEmploymentConfig,
    BiometricsMedicalsConfig,
    ClbTablesConfig,
    CrsCoreConfig,
    CrsTransferabilityConfig,
    LanguageConfig,
    ProgramRulesConfig,
    ProofOfFundsConfig,
    WorkExperienceConfig,
)


class DomainConfigSnapshot(BaseModel):
    """Aggregated, read-only view of domain configs plus documents/forms."""

    crs_core: CrsCoreConfig
    crs_transferability: CrsTransferabilityConfig
    language: LanguageConfig
    clb_tables: ClbTablesConfig
    work_experience: WorkExperienceConfig
    proof_of_funds: ProofOfFundsConfig
    program_rules: ProgramRulesConfig
    arranged_employment: ArrangedEmploymentConfig
    biometrics_medicals: BiometricsMedicalsConfig
    documents: DocumentsConfig
    forms: FormsConfig

    class Config:
        extra = "forbid"


class AdminConfigService:
    """
    Thin read-only facade to expose loaded domain configs to admins/agents.
    """

    def __init__(
        self,
        config_service: ConfigService | None = None,
        document_service: DocumentMatrixService | None = None,
    ) -> None:
        self.config_service = config_service or ConfigService()
        self.document_service = document_service or DocumentMatrixService(self.config_service)

    def _load_domain_bundle(self) -> DomainConfigBundle:
        return self.config_service.load_bundle()

    def _load_document_bundle(self) -> DocumentConfigBundle:
        return self.document_service.get_bundle()

    def get_full_snapshot(self) -> DomainConfigSnapshot:
        domain_bundle = self._load_domain_bundle()
        doc_bundle = self._load_document_bundle()
        return DomainConfigSnapshot(
            crs_core=domain_bundle.crs_core,
            crs_transferability=domain_bundle.crs_transferability,
            language=domain_bundle.language,
            clb_tables=domain_bundle.clb_tables,
            work_experience=domain_bundle.work_experience,
            proof_of_funds=domain_bundle.proof_of_funds,
            program_rules=domain_bundle.program_rules,
            arranged_employment=domain_bundle.arranged_employment,
            biometrics_medicals=domain_bundle.biometrics_medicals,
            documents=doc_bundle.documents,
            forms=doc_bundle.forms,
        )

    def list_sections(self) -> List[str]:
        snapshot = self.get_full_snapshot()
        return list(snapshot.dict().keys())

    def get_section(self, name: str) -> Any:
        snapshot = self.get_full_snapshot()
        if not hasattr(snapshot, name):
            raise KeyError(f"Config section '{name}' not found")
        return getattr(snapshot, name)


