import pytest
from src.scraper import _is_test_posting, _is_clearly_non_dev, _normalize_location

def test_is_test_posting_blocks_test_jobs():
    assert _is_test_posting("TEST JOB", "Fleetio") is True
    assert _is_test_posting("[Test] Demo Role", "Acme") is True
    assert _is_test_posting("Senior Engineer", "TechCorp") is False

def test_is_clearly_non_dev_blocks_categories():
    assert _is_clearly_non_dev("Medical Director", ["healthcare"]) is True
    assert _is_clearly_non_dev("Paid Media Manager", ["marketing"]) is True
    assert _is_clearly_non_dev("Backend Engineer", ["python"]) is False

def test_normalize_location_standardizes_remote():
    assert _normalize_location("Worldwide") == "Remote"
    assert _normalize_location("🌍 Remote") == "Remote"
    assert _normalize_location("United States of America") == "United States"
    assert _normalize_location("UK") == "United Kingdom"
    assert _normalize_location("Kyiv") == "Kyiv"  # Non-standard stays as-is