from __future__ import annotations

from datetime import date, timedelta

from .config_models import DomainRulesConfig, ProofOfFundsConfig, WorkExperienceConfig
from .config_port import RuleConfigPort
from .models import (
    CandidateProfile,
    CRSBreakdown,
    ProgramEvaluationResult,
    RuleFlag,
    Severity,
    WorkExperienceRecord,
)


class RuleEngine:
    """
    Thin skeleton for eligibility + CRS evaluation.
    Pulls thresholds from DomainRulesConfig (config/domain YAML).
    """

    def __init__(
        self, config: DomainRulesConfig | None = None, config_port: RuleConfigPort | None = None
    ) -> None:
        if config_port:
            self.config = config_port.get_config()
        elif config:
            self.config = config
        else:
            raise ValueError("RuleEngine requires DomainRulesConfig or RuleConfigPort")

    def evaluate_candidate(self, profile: CandidateProfile) -> dict[str, ProgramEvaluationResult]:
        results: dict[str, ProgramEvaluationResult] = {
            "FSW": self._evaluate_fsw(profile),
            "CEC": self._evaluate_cec(profile),
        }
        return results

    # --- Internal evaluators ---
    def _evaluate_fsw(self, profile: CandidateProfile) -> ProgramEvaluationResult:
        lang_cfg = self.config.language
        work_cfg = self.config.work_experience
        funds_cfg = self.config.proof_of_funds
        reasons: list[str] = []
        flags: list[RuleFlag] = []

        lang_ok = self._check_language_min_all(profile, lang_cfg.fsw_min_clb, "FSW")
        if not lang_ok:
            reasons.append("FSW_LANG_MIN_CLB")

        work_ok = self._check_continuous_skilled_work(
            profile, work_cfg, program_code="FSW", reasons=reasons
        )

        funds_ok = self._check_funds(profile, funds_cfg, program_code="FSW", reasons=reasons)

        self._add_expiry_flags(profile, flags)

        eligible = lang_ok and work_ok and funds_ok
        crs = self._compute_crs(profile, self.config.crs_core)

        return ProgramEvaluationResult(
            program_code="FSW",
            eligible=eligible,
            reasons=reasons,
            flags=flags,
            crs=crs,
        )

    def _evaluate_cec(self, profile: CandidateProfile) -> ProgramEvaluationResult:
        lang_cfg = self.config.language
        work_cfg = self.config.work_experience
        reasons: list[str] = []
        flags: list[RuleFlag] = []

        canadian_work = [w for w in profile.work_experience if w.is_canadian]
        if not canadian_work:
            reasons.append("CEC_NO_CANADIAN_WORK")
        else:
            months = self._sum_months(canadian_work, recency_years=work_cfg.cec.recency_years)
            if work_cfg.cec.min_canadian_months and months < work_cfg.cec.min_canadian_months:
                reasons.append("CEC_MIN_CANADIAN_MONTHS")

            # Determine TEER bucket of Canadian work (highest skilled)
            teers = [w.teer_level for w in canadian_work if w.teer_level is not None]
            max_teer = min(teers) if teers else None  # lower number = higher skill
            if max_teer is None:
                reasons.append("CEC_UNKNOWN_TEER")
            else:
                lang_ok = self._check_language_cec(profile, max_teer, lang_cfg)
                if not lang_ok:
                    reasons.append("CEC_LANG_MIN_CLB")

        self._add_expiry_flags(profile, flags)
        eligible = len(reasons) == 0
        crs = self._compute_crs(profile, self.config.crs_core)

        return ProgramEvaluationResult(
            program_code="CEC",
            eligible=eligible,
            reasons=reasons,
            flags=flags,
            crs=crs,
        )

    # --- Helpers ---
    def _check_language_min_all(
        self,
        profile: CandidateProfile,
        min_clb: int | None,
        program_code: str,
        reason_prefix: str = "",
    ) -> bool:
        if min_clb is None:
            return True
        best = profile.best_language_test()
        if not best:
            return False
        return best.min_clb() is not None and best.min_clb() >= min_clb

    def _check_language_cec(self, profile: CandidateProfile, teer_level: int, cfg) -> bool:
        best = profile.best_language_test()
        if not best:
            return False
        min_clb = best.min_clb() or 0
        if teer_level in (0, 1):
            threshold = cfg.cec_min_clb_teer_0_1 or 0
        else:
            threshold = cfg.cec_min_clb_teer_2_3 or 0
        return min_clb >= threshold

    def _check_continuous_skilled_work(
        self,
        profile: CandidateProfile,
        work_cfg: WorkExperienceConfig,
        program_code: str,
        reasons: list[str],
    ) -> bool:
        if not profile.work_experience:
            reasons.append(f"{program_code}_NO_WORK")
            return False

        for record in profile.work_experience:
            if work_cfg.eligible_teers and (record.teer_level not in work_cfg.eligible_teers):
                continue
            if not record.is_continuous:
                continue
            months = self._months_between(record.start_date, record.end_date)
            required_months = (
                work_cfg.fsw.min_continuous_months if hasattr(work_cfg, "fsw") else None
            )
            if required_months and months < required_months:
                continue
            return True

        reasons.append(f"{program_code}_WORK_MIN_MONTHS")
        return False

    def _check_funds(
        self,
        profile: CandidateProfile,
        funds_cfg: ProofOfFundsConfig,
        program_code: str,
        reasons: list[str],
    ) -> bool:
        if program_code in funds_cfg.exemptions:
            return True
        if not funds_cfg.table:
            return True
        family_size = profile.family_size or 1
        sorted_table = sorted(funds_cfg.table, key=lambda e: e.family_size)
        target = next((e for e in sorted_table if e.family_size == family_size), sorted_table[-1])
        if not profile.proof_of_funds:
            reasons.append(f"{program_code}_FUNDS_MISSING")
            return False
        latest = max(profile.proof_of_funds, key=lambda p: p.as_of_date)
        if latest.amount >= target.amount_cad:
            return True
        reasons.append(f"{program_code}_FUNDS_INSUFFICIENT")
        return False

    def _add_expiry_flags(self, profile: CandidateProfile, flags: list[RuleFlag]) -> None:
        today = date.today()
        soon = today + timedelta(days=self.config.biometrics_medicals.expiry_warning_days)
        best = profile.best_language_test()
        if best and best.expiry_date and best.expiry_date <= soon:
            flags.append(
                RuleFlag(
                    rule_id="LANG_EXPIRING",
                    severity=Severity.WARNING,
                    message="Language test expiring soon",
                    metadata={"expiry_date": str(best.expiry_date)},
                )
            )
        if (
            profile.medical_status
            and profile.medical_status.expiry_date
            and profile.medical_status.expiry_date <= soon
        ):
            flags.append(
                RuleFlag(
                    rule_id="MEDICAL_EXPIRING",
                    severity=Severity.WARNING,
                    message="Medical exam expiring soon",
                    metadata={"expiry_date": str(profile.medical_status.expiry_date)},
                )
            )

    def _compute_crs(self, profile: CandidateProfile, cfg) -> CRSBreakdown:
        # Placeholder: simple additive model for skeleton/testing only.
        age_points = 0
        age = profile.current_age()
        if age is not None:
            age_points = max(0, cfg.base_age_points - abs(age - 30) * 2)

        lang_points = 0
        best = profile.best_language_test()
        if best and best.min_clb() is not None:
            lang_points = (best.min_clb() or 0) * cfg.language_bonus_per_clb

        core = age_points + lang_points
        return CRSBreakdown(core_points=core)

    def _months_between(self, start: date | None, end: date | None) -> int:
        if not start or not end:
            return 0
        return max(0, (end - start).days // 30)

    def _sum_months(
        self, records: list[WorkExperienceRecord], recency_years: int | None = None
    ) -> int:
        total = 0
        for record in records:
            start = record.start_date
            end = record.end_date or date.today()
            if recency_years:
                cutoff = date.today().replace(year=date.today().year - recency_years)
                if end < cutoff:
                    continue
                start = max(start or cutoff, cutoff)
            total += self._months_between(start, end)
        return total
