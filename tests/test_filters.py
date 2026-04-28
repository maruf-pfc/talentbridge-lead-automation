import pytest
from src.filters import is_dev_role, check_location, passes_filters, normalize

def test_is_dev_role_allows_engineer():
    assert is_dev_role("Senior Backend Engineer") is True
    assert is_dev_role("Frontend Developer") is True
    assert is_dev_role("Full Stack Engineer") is True
    assert is_dev_role("Software Engineer") is True

def test_is_dev_role_blocks_non_dev():
    assert is_dev_role("Medical Director for Health Plan") is False
    assert is_dev_role("Paid Media Manager") is False
    assert is_dev_role("Business Development Director") is False
    assert is_dev_role("UX UI Designer") is False
    assert is_dev_role("Customer Success Manager") is False

def test_is_dev_role_blocks_test_postings():
    """Test that test/demo/sample postings are blocked via BLOCK_TERMS."""
    assert is_dev_role("TEST JOB") is False
    assert is_dev_role("[Test] Demo Position") is False
    assert is_dev_role("Sample Developer Role") is False  # " sample " in BLOCK_TERMS
    assert is_dev_role("Placeholder Engineer") is False

def test_is_dev_role_allows_technical_managers():
    # Exception: technical program managers are okay if they have "engineer"
    assert is_dev_role("Engineering Manager") is True
    assert is_dev_role("Technical Program Manager") is False  # No "engineer" keyword

def test_check_location_valid():
    assert check_location("Remote") == (True, False)
    assert check_location("United States") == (True, False)
    assert check_location("Remote, United States") == (True, False)
    assert check_location("CANADA") == (True, False)
    assert check_location("London, UK") == (True, False)

def test_check_location_unverified():
    """Test that empty/unknown locations return (True, True)."""
    assert check_location("") == (True, True)
    assert check_location("Unknown") == (True, True)
    assert check_location("N/A") == (True, True)  # Normalizes to "na"
    assert check_location("unknown") == (True, True)
    assert check_location("n/a") == (True, True)

def test_check_location_invalid():
    assert check_location("Kyiv") == (False, False)
    assert check_location("Berlin") == (False, False)
    assert check_location("Singapore") == (False, False)
    assert check_location("EMEA") == (False, False)

def test_passes_filters_integration():
    cfg = {}
    # Valid dev role + valid location
    assert passes_filters({
        "title": "Senior Python Engineer",
        "location": "Remote"
    }, cfg) == (True, False)
    
    # Valid dev role + empty location (unverified)
    assert passes_filters({
        "title": "Frontend Developer",
        "location": ""
    }, cfg) == (True, True)
    
    # Non-dev role
    assert passes_filters({
        "title": "Marketing Manager",
        "location": "Remote"
    }, cfg) == (False, False)
    
    # Valid role + invalid location
    assert passes_filters({
        "title": "Backend Engineer",
        "location": "Berlin"
    }, cfg) == (False, False)
    
    # Test posting blocked
    assert passes_filters({
        "title": "[TEST] Demo Job",
        "location": "Remote"
    }, cfg) == (False, False)
    
    # Sample posting blocked via BLOCK_TERMS
    assert passes_filters({
        "title": "Sample Developer Role",
        "location": "Remote"
    }, cfg) == (False, False)