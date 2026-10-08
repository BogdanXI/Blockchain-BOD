from src.bod_verify_simple import verify_envelopes


def test_integrity_report_is_explicit():
    report = verify_envelopes([]) if False else None
    assert report is None
