from __future__ import annotations

from datetime import date, timedelta

from .config_port import CRSConfig, InMemoryRuleConfigPort, RuleConfigPort, WorkRuleConfig
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
    Uses RuleConfigPort for thresholds (currently in-memory stub).
    """

    def __init__(self, config_port: RuleConfigPort | None = None) -> None:
        self.config_port = config_port or InMemoryRuleConfigPort()

    def evaluate_candidate(self, profile: CandidateProfile) -> dict[str, ProgramEvaluationResult]:
        results: dict[str, ProgramEvaluationResult] = {}
        results["FSW"] = self._evaluate_fsw(profile)
        results["CEC"] = self._evaluate_cec(profile)
        # Future: add FST, PNP, etc.
        return results

    # --- Internal evaluators ---
    def _evaluate_fsw(self, profile: CandidateProfile) -> ProgramEvaluationResult:
        cfg = self.config_port.get_program_rules("FSW")
        reasons: list[str] = []
        flags: list[RuleFlag] = []

        lang_ok = self._check_language_min_all(profile, cfg.language.min_clb_all_skills, "FSW")
        if not lang_ok:
            reasons.append("FSW_LANG_MIN_CLB")

        work_ok = self._check_continuous_skilled_work(
            profile, cfg.work, program_code="FSW", reasons=reasons
        )

        funds_ok = self._check_funds(profile, cfg.funds, program_code="FSW", reasons=reasons)

        self._add_expiry_flags(profile, flags)

        eligible = lang_ok and work_ok and funds_ok
        crs = self._compute_crs(profile, self.config_port.get_crs_config())

        return ProgramEvaluationResult(
            program_code="FSW",
            eligible=eligible,
            reasons=reasons,
            flags=flags,
            crs=crs,
        )

    def _evaluate_cec(self, profile: CandidateProfile) -> ProgramEvaluationResult:
        cfg = self.config_port.get_program_rules("CEC")
        reasons: list[str] = []
        flags: list[RuleFlag] = []

        canadian_work = [w for w in profile.work_experience if w.is_canadian]
        if not canadian_work:
            reasons.append("CEC_NO_CANADIAN_WORK")
        else:
            months = self._sum_months(canadian_work, recency_years=cfg.work.recency_years)
            if cfg.work.require_canadian_months and months < cfg.work.require_canadian_months:
                reasons.append("CEC_MIN_CANADIAN_MONTHS")

            # Determine TEER bucket of Canadian work (highest skilled)
            teers = [w.teer_level for w in canadian_work if w.teer_level is not None]
            max_teer = min(teers) if teers else None  # lower number = higher skill
            if max_teer is None:
                reasons.append("CEC_UNKNOWN_TEER")
            else:
                lang_ok = self._check_language_cec(profile, max_teer, cfg.language)
                if not lang_ok:
                    reasons.append("CEC_LANG_MIN_CLB")

        self._add_expiry_flags(profile, flags)
        eligible = len(reasons) == 0
        crs = self._compute_crs(profile, self.config_port.get_crs_config())

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
            threshold = cfg.min_clb_teer_0_1 or 0
        else:
            threshold = cfg.min_clb_teer_2_3 or 0
        return min_clb >= threshold

    def _check_continuous_skilled_work(
        self,
        profile: CandidateProfile,
        work_cfg: WorkRuleConfig,
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
            if work_cfg.min_continuous_months and months < work_cfg.min_continuous_months:
                continue
            return True

        reasons.append(f"{program_code}_WORK_MIN_MONTHS")
        return False

    def _check_funds(
        self, profile: CandidateProfile, funds_cfg, program_code: str, reasons: list[str]
    ) -> bool:
        if funds_cfg.required_amount is None:
            return True
        if funds_cfg.exemptions and program_code in funds_cfg.exemptions:
            return True
        if not profile.proof_of_funds:
            reasons.append(f"{program_code}_FUNDS_MISSING")
            return False
        latest = max(profile.proof_of_funds, key=lambda p: p.as_of_date)
        if latest.amount >= funds_cfg.required_amount:
            return True
        reasons.append(f"{program_code}_FUNDS_INSUFFICIENT")
        return False

    def _add_expiry_flags(self, profile: CandidateProfile, flags: list[RuleFlag]) -> None:
        today = date.today()
        soon = today + timedelta(days=90)
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

    def _compute_crs(self, profile: CandidateProfile, cfg: CRSConfig) -> CRSBreakdown:
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
