from __future__ import annotations

from typing import Callable, Dict

from src.app.domain.crs.models import (
    CRSFactorContribution,
    CRSFactorNLExplanation,
    CRSResult,
)


class CRSExplanationGenerator:
    """
    Simple template-based NL explanations built from structured CRSFactorContribution.
    No IRCC constants are hard-coded; values come from contributions' inputs/thresholds.
    """

    def __init__(self) -> None:
        self.handlers: Dict[str, Callable[[CRSFactorContribution], CRSFactorNLExplanation]] = {
            "core.age.single": self._explain_core_age,
            "core.age.with_spouse": self._explain_core_age,
            "core.education.single": self._explain_core_education,
            "core.education.with_spouse": self._explain_core_education,
            "core.language.first": self._explain_language,
            "core.language.second": self._explain_language,
            "core.canadian_work": self._explain_canadian_work,
            "spouse.education": self._explain_spouse_generic,
            "spouse.language": self._explain_spouse_generic,
            "spouse.canadian_work": self._explain_spouse_generic,
            "transferability.education_language": self._explain_transferability_generic,
            "transferability.education_canadian_work": self._explain_transferability_generic,
            "transferability.foreign_language": self._explain_transferability_generic,
            "transferability.foreign_canadian_work": self._explain_transferability_generic,
            "transferability.certificate_language": self._explain_transferability_generic,
            "additional.provincial_nomination": self._explain_additional_generic,
            "additional.sibling_in_canada": self._explain_additional_generic,
            "additional.canadian_study": self._explain_additional_generic,
            "additional.french_language": self._explain_additional_generic,
            "additional.job_offer": self._explain_additional_generic,
        }

    def apply(self, result: CRSResult) -> CRSResult:
        for contrib in result.factor_contributions:
            code = contrib.explanation.explanation_code if contrib.explanation else ""
            handler = self.handlers.get(code, self._generic)
            contrib.nl_explanation = handler(contrib)
        return result

    def _generic(self, contrib: CRSFactorContribution) -> CRSFactorNLExplanation:
        return CRSFactorNLExplanation(
            explanation_code=contrib.explanation.explanation_code if contrib.explanation else contrib.factor_code,
            title="CRS factor",
            description=f"Points awarded for {contrib.factor_code} based on configuration rule {contrib.rule_reference}.",
            improvement_hint=None,
        )

    def _explain_core_age(self, contrib: CRSFactorContribution) -> CRSFactorNLExplanation:
        exp = contrib.explanation
        band = exp.threshold_summary if exp else {}
        age = exp.input_summary.get("age") if exp else None
        marital = exp.input_summary.get("marital_status") if exp else None
        desc = f"Because you are {age} and marital status is {marital}, points follow the age band {band.get('min_age')}-{band.get('max_age')}."
        hint = "Age points decrease as age rises; other factors can offset loss."
        return CRSFactorNLExplanation(
            explanation_code=exp.explanation_code if exp else contrib.factor_code,
            title="Age factor",
            description=desc,
            improvement_hint=hint,
        )

    def _explain_core_education(self, contrib: CRSFactorContribution) -> CRSFactorNLExplanation:
        exp = contrib.explanation
        level = exp.input_summary.get("education_level") if exp else None
        desc = f"Education level {level} receives {contrib.points_awarded} of {contrib.points_max} possible points."
        hint = "Higher validated education (ECA/Canadian) can raise this score."
        return CRSFactorNLExplanation(
            explanation_code=exp.explanation_code if exp else contrib.factor_code,
            title="Education",
            description=desc,
            improvement_hint=hint,
        )

    def _explain_language(self, contrib: CRSFactorContribution) -> CRSFactorNLExplanation:
        exp = contrib.explanation
        clb = exp.input_summary.get("clb_scores") if exp else {}
        desc = f"Language scores (CLB): {clb} yielded {contrib.points_awarded} points under {exp.rule_path if exp else 'language rules'}."
        hint = "Raising all skills to the next CLB band increases points."
        return CRSFactorNLExplanation(
            explanation_code=exp.explanation_code if exp else contrib.factor_code,
            title="Language",
            description=desc,
            improvement_hint=hint,
        )

    def _explain_canadian_work(self, contrib: CRSFactorContribution) -> CRSFactorNLExplanation:
        exp = contrib.explanation
        years = exp.input_summary.get("canadian_work_experience_years") if exp else None
        desc = f"Canadian work experience of {years} years gives {contrib.points_awarded} points (cap {contrib.points_max})."
        hint = "More authorized Canadian skilled experience can increase this factor."
        return CRSFactorNLExplanation(
            explanation_code=exp.explanation_code if exp else contrib.factor_code,
            title="Canadian Work",
            description=desc,
            improvement_hint=hint,
        )

    def _explain_spouse_generic(self, contrib: CRSFactorContribution) -> CRSFactorNLExplanation:
        exp = contrib.explanation
        desc = f"Spouse factor {contrib.factor_code} awarded {contrib.points_awarded} points."
        hint = "Improving spouse education, language, or Canadian work can raise total CRS."
        return CRSFactorNLExplanation(
            explanation_code=exp.explanation_code if exp else contrib.factor_code,
            title="Spouse factor",
            description=desc,
            improvement_hint=hint,
        )

    def _explain_transferability_generic(self, contrib: CRSFactorContribution) -> CRSFactorNLExplanation:
        exp = contrib.explanation
        desc = f"Transferability combination {exp.explanation_code if exp else contrib.factor_code} awarded {contrib.points_awarded} (cap {contrib.points_max})."
        hint = "Boost both paired factors (e.g., language + education/work) to increase transferability."
        return CRSFactorNLExplanation(
            explanation_code=exp.explanation_code if exp else contrib.factor_code,
            title="Skill transferability",
            description=desc,
            improvement_hint=hint,
        )

    def _explain_additional_generic(self, contrib: CRSFactorContribution) -> CRSFactorNLExplanation:
        exp = contrib.explanation
        desc = f"Additional factor {exp.explanation_code if exp else contrib.factor_code} granted {contrib.points_awarded} points."
        hint = None
        return CRSFactorNLExplanation(
            explanation_code=exp.explanation_code if exp else contrib.factor_code,
            title="Additional points",
            description=desc,
            improvement_hint=hint,
        )

