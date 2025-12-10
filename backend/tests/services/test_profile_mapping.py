from src.app.services.profile_mapping import deep_merge, get_by_path, set_by_path


def test_set_and_get_by_path():
    profile = {}
    updated = set_by_path(profile, "profile.personal.date_of_birth", "1990-01-01")
    assert get_by_path(updated, "profile.personal.date_of_birth") == "1990-01-01"
    # ensure original not mutated
    assert profile == {}


def test_deep_merge():
    base = {"profile": {"personal": {"marital_status": "single"}, "family": {"size": 2}}}
    incoming = {"profile": {"personal": {"citizenship": "CANADA"}, "family": {"size": 3}}}
    merged = deep_merge(base, incoming)
    assert merged["profile"]["personal"]["marital_status"] == "single"
    assert merged["profile"]["personal"]["citizenship"] == "CANADA"
    assert merged["profile"]["family"]["size"] == 3

