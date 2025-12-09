from datetime import date, timedelta

from src.app.rules.config_models import (
    ArrangedEmploymentConfig,
    BiometricsMedicalsConfig,
    ClbTablesConfig,
    CrsCoreConfig,
    CrsTransferabilityConfig,
    DomainRulesConfig,
    LanguageConfig,
    ProgramRule,
    ProgramRulesConfig,
    ProofOfFundsConfig,
    ProofOfFundsEntry,
    WorkExperienceConfig,
    WorkExperienceProgramRule,
)
from src.app.rules.engine import RuleEngine
from src.app.rules.models import (
    CandidateProfile,
    LanguageTestResult,
    ProofOfFundsSnapshot,
    WorkExperienceRecord,
)


def make_language(clb: int) -> LanguageTestResult:
    today = date.today()
    return LanguageTestResult(
        test_type="IELTS",
        test_date=today - timedelta(days=30),
        expiry_date=today + timedelta(days=365),
        listening_clb=clb,
        reading_clb=clb,
        writing_clb=clb,
        speaking_clb=clb,
    )


def make_work(
    teer: int, months: int, canadian: bool = False, continuous: bool = True
) -> WorkExperienceRecord:
    end = date.today()
    start = end - timedelta(days=30 * months)
    return WorkExperienceRecord(
        teer_level=teer,
        start_date=start,
        end_date=end,
        hours_per_week=40,
        is_continuous=continuous,
        is_canadian=canadian,
        is_paid=True,
    )


def make_funds(amount: float) -> ProofOfFundsSnapshot:
    return ProofOfFundsSnapshot(amount=amount, currency="CAD", as_of_date=date.today())


class TestRuleEngine:
    def setup_method(self):
        self.config = DomainRulesConfig(
            crs_core=CrsCoreConfig(base_age_points=50, language_bonus_per_clb=2),
            crs_transferability=CrsTransferabilityConfig(notes="placeholder"),
            language=LanguageConfig(
                fsw_min_clb=7,
                cec_min_clb_teer_0_1=7,
                cec_min_clb_teer_2_3=5,
            ),
            clb_tables=ClbTablesConfig(),
            work_experience=WorkExperienceConfig(
                eligible_teers=[0, 1, 2, 3],
                fsw=WorkExperienceProgramRule(min_continuous_months=12),
                cec=WorkExperienceProgramRule(
                    min_canadian_months=12,
                    recency_years=3,
                ),
            ),
            proof_of_funds=ProofOfFundsConfig(
                table=[
                    ProofOfFundsEntry(family_size=1, amount_cad=13000.0),
                    ProofOfFundsEntry(family_size=2, amount_cad=16000.0),
                ],
                exemptions=["CEC"],
            ),
            program_rules=ProgramRulesConfig(
                programs=[
                    ProgramRule(code="FSW", uses_proof_of_funds=True),
                    ProgramRule(code="CEC", uses_proof_of_funds=False),
                ]
            ),
            arranged_employment=ArrangedEmploymentConfig(
                valid_teers=[0, 1, 2, 3],
                min_duration_months=12,
                require_full_time=True,
                require_non_seasonal=True,
            ),
            biometrics_medicals=BiometricsMedicalsConfig(
                medical_validity_months=12,
                biometrics_validity_months=120,
                expiry_warning_days=90,
            ),
        )
        self.engine = RuleEngine(config=self.config)

    def test_fsw_happy_path(self):
        profile = CandidateProfile(
            date_of_birth=date.today().replace(year=date.today().year - 30),
            language_tests=[make_language(9)],
            work_experience=[make_work(teer=1, months=12)],
            proof_of_funds=[make_funds(20000)],
        )
        results = self.engine.evaluate_candidate(profile)
        fsw = results["FSW"]
        assert fsw.eligible is True
        assert fsw.reasons == []
        assert fsw.crs is not None
        assert fsw.crs.core_points > 0

    def test_fsw_language_failure(self):
        profile = CandidateProfile(
            language_tests=[make_language(6)],
            work_experience=[make_work(teer=1, months=12)],
            proof_of_funds=[make_funds(20000)],
        )
        fsw = self.engine.evaluate_candidate(profile)["FSW"]
        assert fsw.eligible is False
        assert "FSW_LANG_MIN_CLB" in fsw.reasons

    def test_fsw_funds_failure(self):
        profile = CandidateProfile(
            language_tests=[make_language(9)],
            work_experience=[make_work(teer=1, months=12)],
            proof_of_funds=[make_funds(5000)],
        )
        fsw = self.engine.evaluate_candidate(profile)["FSW"]
        assert fsw.eligible is False
        assert "FSW_FUNDS_INSUFFICIENT" in fsw.reasons

    def test_cec_happy_path_teer2(self):
        profile = CandidateProfile(
            language_tests=[make_language(5)],
            work_experience=[make_work(teer=2, months=12, canadian=True)],
            proof_of_funds=[],
        )
        cec = self.engine.evaluate_candidate(profile)["CEC"]
        assert cec.eligible is True
        assert cec.reasons == []

    def test_cec_language_fail_teer0(self):
        profile = CandidateProfile(
            language_tests=[make_language(5)],
            work_experience=[make_work(teer=0, months=12, canadian=True)],
            proof_of_funds=[],
        )
        cec = self.engine.evaluate_candidate(profile)["CEC"]
        assert cec.eligible is False
        assert "CEC_LANG_MIN_CLB" in cec.reasons

    def test_config_drives_pof_threshold(self):
        # Increase PoF and expect failure.
        config_high_pof = self.config.copy()
        config_high_pof.proof_of_funds.table[0].amount_cad = 50000.0
        engine = RuleEngine(config=config_high_pof)
        profile = CandidateProfile(
            language_tests=[make_language(9)],
            work_experience=[make_work(teer=1, months=12)],
            proof_of_funds=[make_funds(20000)],
        )
        fsw = engine.evaluate_candidate(profile)["FSW"]
        assert fsw.eligible is False
        assert "FSW_FUNDS_INSUFFICIENT" in fsw.reasons
