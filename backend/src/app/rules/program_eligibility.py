from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

from src.app.rules.config_models import DomainRulesConfig, ProgramRule, ProofOfFundsConfig, WorkExperienceConfig
from src.app.rules.models import (
    CandidateProfile,
    ProgramEligibilityResult,
    ProgramEligibilitySummary,
)


def _best_language_min_clb(profile: CandidateProfile) -> Optional[int]:
    best = profile.best_language_test()
    return best.min_clb() if best else None


def _months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + (end.month - start.month)


def _sum_months(records: Iterable, recency_years: Optional[int] = None) -> int:
    today = date.today()
    total = 0
    for record in records:
        if not record.start_date or not record.end_date:
            continue
        if recency_years:
            cutoff = date(today.year - recency_years, today.month, today.day)
            if record.end_date < cutoff:
                continue
        total += _months_between(record.start_date, record.end_date)
    return total


def _check_proof_of_funds(profile: CandidateProfile, cfg: ProofOfFundsConfig, program_code: str) -> Optional[str]:
    if program_code in cfg.exemptions:
        return None
    if not cfg.table:
        return None
    family_size = profile.family_size or 1
    sorted_table = sorted(cfg.table, key=lambda e: e.family_size)
    target = next((e for e in sorted_table if e.family_size == family_size), sorted_table[-1])
    if not profile.proof_of_funds:
        return "Proof of funds missing"
    latest = max(profile.proof_of_funds, key=lambda p: p.as_of_date)
    if latest.amount >= target.amount_cad:
        return None
    return "Proof of funds insufficient"


def _fsw_eligibility(profile: CandidateProfile, cfg: DomainRulesConfig, program_rule: ProgramRule) -> ProgramEligibilityResult:
    reasons: list[str] = []
    warnings: list[str] = []

    min_clb = cfg.language.fsw_min_clb
    best_clb = _best_language_min_clb(profile)
    if min_clb and (best_clb is None or best_clb < min_clb):
        reasons.append(f"FSW: minimum CLB {min_clb} required; best={best_clb or 'N/A'}")

    # Work: continuous skilled work using work_experience config
    work_cfg = cfg.work_experience
    continuous_ok = False
    for record in profile.work_experience:
        if work_cfg.eligible_teers and (record.teer_level not in work_cfg.eligible_teers):
            continue
        if not record.is_continuous or not record.start_date or not record.end_date:
            continue
        months = _months_between(record.start_date, record.end_date)
        required = work_cfg.fsw.min_continuous_months
        if required and months < required:
            continue
        continuous_ok = True
        break
    if not continuous_ok:
        reasons.append("FSW: insufficient continuous skilled work per config")

    # Education: require at least one record (config-driven level matching can be extended later)
    if program_rule.min_education_level and not profile.education:
        reasons.append("FSW: education evidence missing")

    # Proof of funds
    pof_reason = _check_proof_of_funds(profile, cfg.proof_of_funds, "FSW")
    if pof_reason:
        reasons.append(f"FSW: {pof_reason}")

    eligible = len(reasons) == 0
    return ProgramEligibilityResult(
        program_code="FSW",
        eligible=eligible,
        reasons=reasons,
        warnings=warnings,
    )


def _cec_eligibility(profile: CandidateProfile, cfg: DomainRulesConfig, program_rule: ProgramRule) -> ProgramEligibilityResult:
    reasons: list[str] = []
    warnings: list[str] = []

    work_cfg = cfg.work_experience
    canadian_work = [w for w in profile.work_experience if w.is_canadian]
    if not canadian_work:
        reasons.append("CEC: no Canadian work experience")
    else:
        months = _sum_months(canadian_work, recency_years=work_cfg.cec.recency_years)
        if work_cfg.cec.min_canadian_months and months < work_cfg.cec.min_canadian_months:
            reasons.append("CEC: insufficient Canadian work months")

        teers = [w.teer_level for w in canadian_work if w.teer_level is not None]
        max_teer = min(teers) if teers else None
        best_clb = _best_language_min_clb(profile) or 0
        if max_teer in (0, 1):
            threshold = cfg.language.cec_min_clb_teer_0_1 or 0
        else:
            threshold = cfg.language.cec_min_clb_teer_2_3 or 0
        if best_clb < threshold:
            reasons.append(f"CEC: CLB below threshold {threshold} for TEER bucket")

    # Proof of funds (generally exempt for CEC, but honor config)
    if program_rule.uses_proof_of_funds:
        pof_reason = _check_proof_of_funds(profile, cfg.proof_of_funds, "CEC")
        if pof_reason:
            reasons.append(f"CEC: {pof_reason}")

    eligible = len(reasons) == 0
    return ProgramEligibilityResult(program_code="CEC", eligible=eligible, reasons=reasons, warnings=warnings)


def _fst_eligibility(profile: CandidateProfile, cfg: DomainRulesConfig, program_rule: ProgramRule) -> ProgramEligibilityResult:
    reasons: list[str] = []
    warnings: list[str] = []

    best_clb = _best_language_min_clb(profile) or 0
    speak_listen = cfg.language.fst_min_clb_speak_listen or 0
    read_write = cfg.language.fst_min_clb_read_write or 0
    if best_clb < min(speak_listen, read_write):
        reasons.append(
            f"FST: CLB below required thresholds (speak/listen {speak_listen}, read/write {read_write})"
        )

    if program_rule.requires_certificate_or_offer:
        has_offer = any(profile.job_offers)
        if not has_offer:
            reasons.append("FST: requires job offer or trade certificate per config")

    # Proof of funds if required
    if program_rule.uses_proof_of_funds:
        pof_reason = _check_proof_of_funds(profile, cfg.proof_of_funds, "FST")
        if pof_reason:
            reasons.append(f"FST: {pof_reason}")

    eligible = len(reasons) == 0
    return ProgramEligibilityResult(program_code="FST", eligible=eligible, reasons=reasons, warnings=warnings)


def evaluate_programs(profile: CandidateProfile, cfg: DomainRulesConfig) -> ProgramEligibilitySummary:
    program_rules = {p.code: p for p in cfg.program_rules.programs}
    results: list[ProgramEligibilityResult] = []

    if "FSW" in program_rules:
        results.append(_fsw_eligibility(profile, cfg, program_rules["FSW"]))
    if "CEC" in program_rules:
        results.append(_cec_eligibility(profile, cfg, program_rules["CEC"]))
    if "FST" in program_rules:
        results.append(_fst_eligibility(profile, cfg, program_rules["FST"]))

    return ProgramEligibilitySummary(results=results)

