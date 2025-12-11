from src.app.heuristics.document_heuristics import DocumentHeuristicsEngine


class DummyDoc:
    def __init__(self, id="doc-1", document_type="passport_main", filename="passport_2018.pdf", mime_type="application/pdf", file_size=6000):
        self.id = id
        self.document_type = document_type
        self.filename = filename
        self.mime_type = mime_type
        self.file_size = file_size


class DummyReq:
    def __init__(self, id="passport_main"):
        self.id = id
        self.label = id
        self.category = "identity"


def test_missing_keywords_detected():
    engine = DocumentHeuristicsEngine()
    doc = DummyDoc()
    req = DummyReq()
    findings = engine.analyze(
        doc_definition=req,
        uploaded_doc=doc,
        ocr_text="This is a Passport document with Number only",
        canonical_profile={},
    )
    assert any(f["finding_code"].endswith("missing_keywords") for f in findings)


def test_expired_filename_year_flagged():
    engine = DocumentHeuristicsEngine()
    doc = DummyDoc(filename="passport_2015_scan.pdf")
    req = DummyReq()
    findings = engine.analyze(
        doc_definition=req,
        uploaded_doc=doc,
        ocr_text=None,
        canonical_profile={},
    )
    assert any(f["finding_code"].endswith("possibly_expired") for f in findings)


def test_name_mismatch_against_profile():
    engine = DocumentHeuristicsEngine()
    doc = DummyDoc(filename="passport_2024.pdf")
    req = DummyReq()
    findings = engine.analyze(
        doc_definition=req,
        uploaded_doc=doc,
        ocr_text="Passport for Jordan Smith",
        canonical_profile={"profile": {"personal": {"given_name": "Alex", "family_name": "Doe"}}},
    )
    assert any(f["finding_code"].endswith("name_mismatch") for f in findings)

