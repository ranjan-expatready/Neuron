from __future__ import annotations

from typing import List, Tuple

from src.app.domain.crs.models import (
    CRSFactorContribution,
    CRSFactorExplanation,
    CRSProfileInput,
    CRSResult,
    EducationLevel,
    LanguageCLBProfile,
)
from src.app.rules.config_models import (
    CrsAdditionalPointsConfig,
    CrsCoreConfig,
    CrsSpouseConfig,
    CrsTransferabilityConfig,
    DomainRulesConfig,
    TransferabilityEntry,
)


class CRSEngine:
    """
    Config-first CRS calculator for Express Entry.
    All point values come from config/domain/crs.yaml (loaded via DomainRulesConfig).
    """

    def __init__(self, config: DomainRulesConfig) -> None:
        self.config = config

    def compute(self, profile: CRSProfileInput) -> CRSResult:
        contributions: List[CRSFactorContribution] = []
        contributions.extend(self._compute_core(profile))
        contributions.extend(self._compute_spouse(profile))
        contributions.extend(self._compute_transferability(profile))
        contributions.extend(self._compute_additional(profile))
        total = sum(c.points_awarded for c in contributions)
        return CRSResult(total_score=total, factor_contributions=contributions)

    def _make_explanation(
        self,
        explanation_code: str,
        rule_path: str,
        input_summary: dict,
        threshold_summary: dict,
        notes: dict | None = None,
    ) -> CRSFactorExplanation:
        return CRSFactorExplanation(
            explanation_code=explanation_code,
            rule_path=rule_path,
            input_summary=input_summary,
            threshold_summary=threshold_summary,
            notes=notes,
        )

    # --- Core human capital ---
    def _compute_core(self, profile: CRSProfileInput) -> List[CRSFactorContribution]:
        cfg: CrsCoreConfig = self.config.crs_core
        with_spouse = profile.marital_status.with_spouse
        factors: List[CRSFactorContribution] = []

        age_points, age_max = self._lookup_age_points(profile.age, cfg, with_spouse)
        age_band = self._age_band(profile.age, cfg)
        factors.append(
            CRSFactorContribution(
                factor_code="core_human_capital_age",
                points_awarded=age_points,
                points_max=age_max,
                inputs_used={"age": profile.age, "with_spouse": with_spouse},
                rule_reference="crs_core.age_bands",
                explanation=self._make_explanation(
                    "core.age.with_spouse" if with_spouse else "core.age.single",
                    "crs_core.age_bands",
                    {"age": profile.age, "marital_status": profile.marital_status.value},
                    age_band or {},
                ),
            )
        )

        edu_points, edu_max = self._lookup_education_points(
            profile.education_level, cfg, with_spouse
        )
        factors.append(
            CRSFactorContribution(
                factor_code="core_human_capital_education",
                points_awarded=edu_points,
                points_max=edu_max,
                inputs_used={"education_level": profile.education_level},
                rule_reference="crs_core.education",
                explanation=self._make_explanation(
                    "core.education.with_spouse" if with_spouse else "core.education.single",
                    "crs_core.education",
                    {"education_level": profile.education_level.value, "marital_status": profile.marital_status.value},
                    {"points": edu_points, "points_max": edu_max},
                ),
            )
        )

        first_lang_points, first_lang_max = self._compute_language_points(
            profile.first_official_language, cfg.first_official_language, with_spouse
        )
        factors.append(
            CRSFactorContribution(
                factor_code="core_human_capital_first_official_language",
                points_awarded=first_lang_points,
                points_max=first_lang_max,
                inputs_used={
                    "first_language": profile.first_official_language.dict(),
                    "with_spouse": with_spouse,
                },
                rule_reference="crs_core.first_official_language",
                explanation=self._make_explanation(
                    "core.language.first",
                    "crs_core.first_official_language",
                    {
                        "with_spouse": with_spouse,
                        "clb_scores": profile.first_official_language.dict(),
                    },
                    {"per_skill_points_max": first_lang_max},
                ),
            )
        )

        second_lang_points = 0
        second_lang_max = cfg.second_official_language.max_points_with_spouse if with_spouse else cfg.second_official_language.max_points_single
        if profile.second_official_language:
            second_lang_points = self._compute_second_language_points(
                profile.second_official_language, cfg, with_spouse
            )
        factors.append(
            CRSFactorContribution(
                factor_code="core_human_capital_second_official_language",
                points_awarded=min(second_lang_points, second_lang_max),
                points_max=second_lang_max,
                inputs_used={
                    "second_language": profile.second_official_language.dict()
                    if profile.second_official_language
                    else None,
                    "with_spouse": with_spouse,
                },
                rule_reference="crs_core.second_official_language",
                explanation=self._make_explanation(
                    "core.language.second",
                    "crs_core.second_official_language",
                    {
                        "with_spouse": with_spouse,
                        "clb_scores": profile.second_official_language.dict()
                        if profile.second_official_language
                        else None,
                    },
                    {"cap": second_lang_max},
                ),
            )
        )

        can_work_points, can_work_max = self._lookup_canadian_work_points(
            profile.canadian_work_experience_years, cfg, with_spouse
        )
        factors.append(
            CRSFactorContribution(
                factor_code="core_human_capital_canadian_work",
                points_awarded=can_work_points,
                points_max=can_work_max,
                inputs_used={
                    "canadian_work_experience_years": profile.canadian_work_experience_years,
                    "with_spouse": with_spouse,
                },
                rule_reference="crs_core.canadian_work_experience",
                explanation=self._make_explanation(
                    "core.canadian_work",
                    "crs_core.canadian_work_experience",
                    {
                        "canadian_work_years": profile.canadian_work_experience_years,
                        "with_spouse": with_spouse,
                    },
                    {"points": can_work_points, "points_max": can_work_max},
                ),
            )
        )

        return factors

    # --- Spouse factors ---
    def _compute_spouse(self, profile: CRSProfileInput) -> List[CRSFactorContribution]:
        if not profile.marital_status.with_spouse:
            return []
        cfg: CrsSpouseConfig = self.config.crs_spouse
        factors: List[CRSFactorContribution] = []

        edu_points = 0
        edu_max = max((row.points for row in cfg.education), default=0)
        if profile.spouse_education_level:
            edu_points = self._match_points_by_level(
                profile.spouse_education_level, cfg.education
            )
        factors.append(
            CRSFactorContribution(
                factor_code="spouse_education",
                points_awarded=edu_points,
                points_max=edu_max,
                inputs_used={"spouse_education_level": profile.spouse_education_level},
                rule_reference="crs_spouse.education",
                explanation=self._make_explanation(
                    "spouse.education",
                    "crs_spouse.education",
                    {"spouse_education_level": profile.spouse_education_level.value if profile.spouse_education_level else None},
                    {"points": edu_points, "points_max": edu_max},
                ),
            )
        )

        lang_points = 0
        lang_max = len(["reading", "writing", "listening", "speaking"]) * max(
            (row.points_per_skill for row in cfg.language), default=0
        )
        if profile.spouse_language:
            lang_points = self._compute_spouse_language_points(
                profile.spouse_language, cfg
            )
        factors.append(
            CRSFactorContribution(
                factor_code="spouse_language",
                points_awarded=lang_points,
                points_max=lang_max,
                inputs_used={"spouse_language": profile.spouse_language.dict() if profile.spouse_language else None},
                rule_reference="crs_spouse.language",
                explanation=self._make_explanation(
                    "spouse.language",
                    "crs_spouse.language",
                    {"spouse_language": profile.spouse_language.dict() if profile.spouse_language else None},
                    {"points": lang_points, "points_max": lang_max},
                ),
            )
        )

        work_points = 0
        work_max = max((row.points for row in cfg.canadian_work_experience), default=0)
        if profile.spouse_canadian_work_experience_years is not None:
            work_points = self._match_points_by_years(
                profile.spouse_canadian_work_experience_years, cfg.canadian_work_experience
            )
        factors.append(
            CRSFactorContribution(
                factor_code="spouse_canadian_work",
                points_awarded=work_points,
                points_max=work_max,
                inputs_used={
                    "spouse_canadian_work_experience_years": profile.spouse_canadian_work_experience_years
                },
                rule_reference="crs_spouse.canadian_work_experience",
                explanation=self._make_explanation(
                    "spouse.canadian_work",
                    "crs_spouse.canadian_work_experience",
                    {"spouse_canadian_work_years": profile.spouse_canadian_work_experience_years},
                    {"points": work_points, "points_max": work_max},
                ),
            )
        )
        return factors

    # --- Transferability ---
    def _compute_transferability(self, profile: CRSProfileInput) -> List[CRSFactorContribution]:
        cfg: CrsTransferabilityConfig = self.config.crs_transferability
        factors: List[CRSFactorContribution] = []

        clb_min = profile.first_official_language.min_clb()
        clb_band = self._language_band_for_transferability(clb_min)
        edu_key = self._education_transfer_key(profile.education_level)
        can_work_bucket = self._canadian_work_bucket(profile.canadian_work_experience_years)
        foreign_work_bucket = self._foreign_work_bucket(profile.foreign_work_experience_years)

        # Education + Language
        edu_lang_points = self._sum_transfer_points(
            cfg.education_language, edu_key, clb_band
        )
        edu_lang_points = min(edu_lang_points, cfg.caps.per_bundle)
        factors.append(
            CRSFactorContribution(
                factor_code="transferability_education_language",
                points_awarded=edu_lang_points,
                points_max=cfg.caps.per_bundle,
                inputs_used={"education_key": edu_key, "clb_band": clb_band},
                rule_reference="crs_transferability.education_language",
                explanation=self._make_explanation(
                    "transferability.education_language",
                    "crs_transferability.education_language",
                    {"education_key": edu_key, "clb_band": clb_band},
                    {"cap": cfg.caps.per_bundle, "points_awarded": edu_lang_points},
                ),
            )
        )

        # Education + Canadian work
        edu_can_work_points = self._sum_transfer_points(
            cfg.education_canadian_work, edu_key, can_work_bucket
        )
        edu_can_work_points = min(edu_can_work_points, cfg.caps.per_bundle)
        factors.append(
            CRSFactorContribution(
                factor_code="transferability_education_canadian_work",
                points_awarded=edu_can_work_points,
                points_max=cfg.caps.per_bundle,
                inputs_used={
                    "education_key": edu_key,
                    "canadian_work_bucket": can_work_bucket,
                },
                rule_reference="crs_transferability.education_canadian_work",
                explanation=self._make_explanation(
                    "transferability.education_canadian_work",
                    "crs_transferability.education_canadian_work",
                    {"education_key": edu_key, "canadian_work_bucket": can_work_bucket},
                    {"cap": cfg.caps.per_bundle, "points_awarded": edu_can_work_points},
                ),
            )
        )

        # Foreign work + Language
        foreign_lang_points = self._sum_transfer_points(
            cfg.foreign_language, foreign_work_bucket, clb_band
        )
        foreign_lang_points = min(foreign_lang_points, cfg.caps.per_bundle)
        factors.append(
            CRSFactorContribution(
                factor_code="transferability_foreign_work_language",
                points_awarded=foreign_lang_points,
                points_max=cfg.caps.per_bundle,
                inputs_used={
                    "foreign_work_bucket": foreign_work_bucket,
                    "clb_band": clb_band,
                },
                rule_reference="crs_transferability.foreign_language",
                explanation=self._make_explanation(
                    "transferability.foreign_language",
                    "crs_transferability.foreign_language",
                    {"foreign_work_bucket": foreign_work_bucket, "clb_band": clb_band},
                    {"cap": cfg.caps.per_bundle, "points_awarded": foreign_lang_points},
                ),
            )
        )

        # Foreign work + Canadian work
        foreign_can_points = self._sum_transfer_points(
            cfg.foreign_canadian_work, foreign_work_bucket, can_work_bucket
        )
        foreign_can_points = min(foreign_can_points, cfg.caps.per_bundle)
        factors.append(
            CRSFactorContribution(
                factor_code="transferability_foreign_work_canadian_work",
                points_awarded=foreign_can_points,
                points_max=cfg.caps.per_bundle,
                inputs_used={
                    "foreign_work_bucket": foreign_work_bucket,
                    "canadian_work_bucket": can_work_bucket,
                },
                rule_reference="crs_transferability.foreign_canadian_work",
                explanation=self._make_explanation(
                    "transferability.foreign_canadian_work",
                    "crs_transferability.foreign_canadian_work",
                    {"foreign_work_bucket": foreign_work_bucket, "canadian_work_bucket": can_work_bucket},
                    {"cap": cfg.caps.per_bundle, "points_awarded": foreign_can_points},
                ),
            )
        )

        # Certificate + Language
        cert_points = 0
        if profile.has_certificate_of_qualification:
            cert_band = self._certificate_language_band(clb_min)
            cert_points = self._sum_transfer_points(
                cfg.certificate_language, "certificate_present", cert_band
            )
        cert_points = min(cert_points, cfg.caps.per_bundle)
        factors.append(
            CRSFactorContribution(
                factor_code="transferability_certificate_language",
                points_awarded=cert_points,
                points_max=cfg.caps.per_bundle,
                inputs_used={
                    "has_certificate_of_qualification": profile.has_certificate_of_qualification,
                    "clb_band": self._certificate_language_band(clb_min) if profile.has_certificate_of_qualification else None,
                },
                rule_reference="crs_transferability.certificate_language",
                explanation=self._make_explanation(
                    "transferability.certificate_language",
                    "crs_transferability.certificate_language",
                    {
                        "has_certificate_of_qualification": profile.has_certificate_of_qualification,
                        "clb_band": self._certificate_language_band(clb_min) if profile.has_certificate_of_qualification else None,
                    },
                    {"cap": cfg.caps.per_bundle, "points_awarded": cert_points},
                ),
            )
        )

        # Enforce overall cap
        transfer_total = sum(f.points_awarded for f in factors)
        if transfer_total > cfg.caps.total:
            scale_down = cfg.caps.total / transfer_total if transfer_total else 0
            for idx, f in enumerate(factors):
                adjusted = int(f.points_awarded * scale_down)
                factors[idx] = f.copy(update={"points_awarded": adjusted})

        return factors

    # --- Additional points ---
    def _compute_additional(self, profile: CRSProfileInput) -> List[CRSFactorContribution]:
        cfg: CrsAdditionalPointsConfig = self.config.crs_additional
        factors: List[CRSFactorContribution] = []

        pnp_points = cfg.provincial_nomination if profile.has_provincial_nomination else 0
        factors.append(
            CRSFactorContribution(
                factor_code="additional_provincial_nomination",
                points_awarded=pnp_points,
                points_max=cfg.provincial_nomination,
                inputs_used={"has_provincial_nomination": profile.has_provincial_nomination},
                rule_reference="crs_additional.provincial_nomination",
                explanation=self._make_explanation(
                    "additional.provincial_nomination",
                    "crs_additional.provincial_nomination",
                    {"has_provincial_nomination": profile.has_provincial_nomination},
                    {"points": pnp_points, "points_max": cfg.provincial_nomination},
                ),
            )
        )

        sibling_points = cfg.sibling_in_canada if profile.has_sibling_in_canada else 0
        factors.append(
            CRSFactorContribution(
                factor_code="additional_sibling_in_canada",
                points_awarded=sibling_points,
                points_max=cfg.sibling_in_canada,
                inputs_used={"has_sibling_in_canada": profile.has_sibling_in_canada},
                rule_reference="crs_additional.sibling_in_canada",
                explanation=self._make_explanation(
                    "additional.sibling_in_canada",
                    "crs_additional.sibling_in_canada",
                    {"has_sibling_in_canada": profile.has_sibling_in_canada},
                    {"points": sibling_points, "points_max": cfg.sibling_in_canada},
                ),
            )
        )

        study_points = 0
        study_max = cfg.canadian_study.three_or_more_years
        if profile.canadian_study_years:
            if profile.canadian_study_years >= 3:
                study_points = cfg.canadian_study.three_or_more_years
            elif profile.canadian_study_years >= 1:
                study_points = cfg.canadian_study.one_to_two_years
        factors.append(
            CRSFactorContribution(
                factor_code="additional_canadian_study",
                points_awarded=study_points,
                points_max=study_max,
                inputs_used={"canadian_study_years": profile.canadian_study_years},
                rule_reference="crs_additional.canadian_study",
                explanation=self._make_explanation(
                    "additional.canadian_study",
                    "crs_additional.canadian_study",
                    {"canadian_study_years": profile.canadian_study_years},
                    {"points": study_points, "points_max": study_max},
                ),
            )
        )

        french_points = self._compute_french_bonus(profile, cfg)
        french_max = max((entry.points for entry in cfg.french), default=0)
        factors.append(
            CRSFactorContribution(
                factor_code="additional_french_language",
                points_awarded=french_points,
                points_max=french_max,
                inputs_used={
                    "first_language_is_french": profile.first_language_is_french,
                    "second_language_present": profile.second_official_language is not None,
                },
                rule_reference="crs_additional.french",
                explanation=self._make_explanation(
                    "additional.french_language",
                    "crs_additional.french",
                    {
                        "first_language_is_french": profile.first_language_is_french,
                        "second_language_present": profile.second_official_language is not None,
                    },
                    {"points": french_points, "points_max": french_max},
                ),
            )
        )

        job_offer_points = 0
        job_offer_max = max((entry.points for entry in cfg.job_offer), default=0)
        if profile.has_valid_job_offer and profile.job_offer_teer_category:
            job_offer_points = self._job_offer_points(profile.job_offer_teer_category, cfg)
        factors.append(
            CRSFactorContribution(
                factor_code="additional_job_offer",
                points_awarded=job_offer_points,
                points_max=job_offer_max,
                inputs_used={
                    "has_valid_job_offer": profile.has_valid_job_offer,
                    "job_offer_teer_category": profile.job_offer_teer_category,
                },
                rule_reference="crs_additional.job_offer",
                explanation=self._make_explanation(
                    "additional.job_offer",
                    "crs_additional.job_offer",
                    {
                        "has_valid_job_offer": profile.has_valid_job_offer,
                        "job_offer_teer_category": profile.job_offer_teer_category,
                    },
                    {"points": job_offer_points, "points_max": job_offer_max},
                ),
            )
        )

        return factors

    # --- Helpers ---
    def _lookup_age_points(
        self, age: int, cfg: CrsCoreConfig, with_spouse: bool
    ) -> Tuple[int, int]:
        for band in cfg.age_bands:
            if band.min_age <= age <= band.max_age:
                return (band.with_spouse if with_spouse else band.single, self._max_age_points(cfg, with_spouse))
        return (0, self._max_age_points(cfg, with_spouse))

    def _age_band(self, age: int, cfg: CrsCoreConfig) -> dict | None:
        for band in cfg.age_bands:
            if band.min_age <= age <= band.max_age:
                return {
                    "min_age": band.min_age,
                    "max_age": band.max_age,
                    "single": band.single,
                    "with_spouse": band.with_spouse,
                }
        return None

    def _max_age_points(self, cfg: CrsCoreConfig, with_spouse: bool) -> int:
        return max((band.with_spouse if with_spouse else band.single for band in cfg.age_bands), default=0)

    def _lookup_education_points(
        self, level: EducationLevel, cfg: CrsCoreConfig, with_spouse: bool
    ) -> Tuple[int, int]:
        points = 0
        max_points = max((row.with_spouse if with_spouse else row.single for row in cfg.education), default=0)
        for row in cfg.education:
            if row.level == level.value:
                points = row.with_spouse if with_spouse else row.single
                break
        return points, max_points

    def _compute_language_points(
        self,
        lang: LanguageCLBProfile,
        rows,
        with_spouse: bool,
    ) -> Tuple[int, int]:
        per_skill_max = max((r.with_spouse_per_skill if with_spouse else r.single_per_skill for r in rows), default=0)
        total_max = per_skill_max * 4
        values = [lang.reading, lang.writing, lang.listening, lang.speaking]
        points = 0
        for clb in values:
            points += self._per_skill_points(clb, rows, with_spouse)
        return points, total_max

    def _per_skill_points(self, clb: int, rows, with_spouse: bool) -> int:
        eligible_rows = sorted(rows, key=lambda r: r.clb)
        chosen = 0
        for row in eligible_rows:
            if clb >= row.clb:
                chosen = row.with_spouse_per_skill if with_spouse else row.single_per_skill
        return chosen

    def _compute_second_language_points(
        self, lang: LanguageCLBProfile, cfg: CrsCoreConfig, with_spouse: bool
    ) -> int:
        rows = cfg.second_official_language.rows
        values = [lang.reading, lang.writing, lang.listening, lang.speaking]
        points = sum(self._per_skill_points(clb, rows, with_spouse) for clb in values)
        cap = cfg.second_official_language.max_points_with_spouse if with_spouse else cfg.second_official_language.max_points_single
        return min(points, cap)

    def _lookup_canadian_work_points(
        self, years: int, cfg: CrsCoreConfig, with_spouse: bool
    ) -> Tuple[int, int]:
        rows = sorted(cfg.canadian_work_experience, key=lambda r: r.years)
        points = 0
        for row in rows:
            if years >= row.years:
                points = row.with_spouse if with_spouse else row.single
        max_points = max((row.with_spouse if with_spouse else row.single for row in rows), default=0)
        return points, max_points

    def _match_points_by_level(self, level: EducationLevel, rows) -> int:
        for row in rows:
            if row.level == level.value:
                return row.points
        return 0

    def _compute_spouse_language_points(
        self, lang: LanguageCLBProfile, cfg: CrsSpouseConfig
    ) -> int:
        rows = sorted(cfg.language, key=lambda r: r.clb)
        values = [lang.reading, lang.writing, lang.listening, lang.speaking]
        points = 0
        for clb in values:
            chosen = 0
            for row in rows:
                if clb >= row.clb:
                    chosen = row.points_per_skill
            points += chosen
        return points

    def _match_points_by_years(self, years: int, rows) -> int:
        chosen = 0
        for row in sorted(rows, key=lambda r: r.years):
            if years >= row.years:
                chosen = row.points
        return chosen

    def _education_transfer_key(self, level: EducationLevel) -> str:
        mapping = {
            EducationLevel.LESS_THAN_SECONDARY: "high_school_or_less",
            EducationLevel.SECONDARY: "high_school_or_less",
            EducationLevel.ONE_YEAR_POST_SECONDARY: "postsec_1yr_plus",
            EducationLevel.TWO_YEAR_POST_SECONDARY: "postsec_1yr_plus",
            EducationLevel.BACHELOR_THREE_YEAR_PLUS: "postsec_1yr_plus",
            EducationLevel.TWO_OR_MORE_CREDENTIALS: "two_or_more_creds_one_3yr_plus",
            EducationLevel.MASTERS_OR_PROFESSIONAL: "masters_or_entry_to_practice",
            EducationLevel.DOCTORATE: "doctorate",
        }
        return mapping.get(level, "high_school_or_less")

    def _language_band_for_transferability(self, clb_min: int) -> str:
        if clb_min >= 9:
            return "clb9_plus"
        if clb_min >= 7:
            return "clb7_to_clb8"
        return "below_7"

    def _certificate_language_band(self, clb_min: int) -> str:
        if clb_min >= 7:
            return "clb7_plus"
        if clb_min >= 5:
            return "clb5_to_clb6"
        return "below_5"

    def _canadian_work_bucket(self, years: int) -> str:
        if years >= 2:
            return "two_years_plus"
        if years >= 1:
            return "one_year"
        return "none"

    def _foreign_work_bucket(self, years: int) -> str:
        if years >= 3:
            return "three_or_more_years"
        if years >= 1:
            return "one_to_two_years"
        return "none"

    def _sum_transfer_points(
        self, rows: List[TransferabilityEntry], factor_one: str, factor_two: str
    ) -> int:
        for row in rows:
            if row.factor_one == factor_one and row.factor_two == factor_two:
                return row.points
        return 0

    def _compute_french_bonus(
        self, profile: CRSProfileInput, cfg: CrsAdditionalPointsConfig
    ) -> int:
        french_min = None
        english_min = None
        if profile.first_language_is_french:
            french_min = profile.first_official_language.min_clb()
            if profile.second_official_language:
                english_min = profile.second_official_language.min_clb()
        else:
            if profile.second_official_language and profile.second_official_language.min_clb() is not None:
                french_min = profile.second_official_language.min_clb()
            english_min = profile.first_official_language.min_clb()

        if french_min is None:
            return 0

        points = 0
        for entry in cfg.french:
            if entry.condition == "nclc7_plus_and_english_clb4_or_less":
                if french_min >= 7 and (english_min is None or english_min <= 4):
                    points = max(points, entry.points)
            elif entry.condition == "nclc7_plus_and_english_clb5_plus":
                if french_min >= 7 and english_min is not None and english_min >= 5:
                    points = max(points, entry.points)
        return points

    def _job_offer_points(self, teer_category: str, cfg: CrsAdditionalPointsConfig) -> int:
        for entry in cfg.job_offer:
            if entry.teer_category == teer_category:
                return entry.points
        return 0

