from __future__ import annotations

from typing import Any, Dict, Optional

from src.app.domain.crs.models import CRSProfileInput, CRSResult
from src.app.domain_config.service import ConfigService
from src.app.observability.logging import get_logger, log_error, log_info
from src.app.observability.metrics import metrics_registry
from src.app.rules.crs_adapter import build_crs_profile_from_candidate
from src.app.rules.crs_engine import CRSEngine
from src.app.rules.models import CandidateProfile


class CRSEngineService:
    """
    Public service wrapper for the CRS engine with observability hooks.
    """

    def __init__(self, config_service: Optional[ConfigService] = None) -> None:
        self.config_service = config_service or ConfigService()
        self.engine = CRSEngine(config=self.config_service.get_domain_rules())
        self.logger = get_logger(__name__)

    def compute_for_profile(
        self, crs_profile: CRSProfileInput, *, context: Optional[Dict[str, Any]] = None
    ) -> CRSResult:
        context = context or {}
        try:
            result = self.engine.compute(crs_profile)
            metrics_registry.record_crs_evaluation(True)
            log_info(
                logger=self.logger,
                message="CRS computation completed",
                component="crs_engine",
                extra_fields={
                    "total_score": result.total_score,
                    "num_factors": len(result.factor_contributions),
                    **context,
                },
            )
            return result
        except Exception as exc:
            metrics_registry.record_crs_evaluation(False)
            log_error(
                logger=self.logger,
                message="CRS computation failed",
                component="crs_engine",
                extra_fields={"error": str(exc), **context},
            )
            raise

    def compute_for_candidate(
        self, candidate_profile: CandidateProfile, *, context: Optional[Dict[str, Any]] = None
    ) -> CRSResult:
        crs_profile = build_crs_profile_from_candidate(candidate_profile)
        return self.compute_for_profile(crs_profile, context=context)

