import pytest
from src.filters import is_dev_role, passes_filters

def test_is_dev_role_allows_engineer():
    assert is_dev_role("Senior Backend Engineer", ["python", "aws"]) is True
    assert is_dev_role("Frontend Developer", ["react", "javascript"]) is True
    assert is_dev_role("Full Stack Engineer", ["node", "react"]) is True

def test_is_dev_role_blocks_non_dev():
    assert is_dev_role("Medical Director for Health Plan", ["healthcare"]) is False
    assert is_dev_role("Paid Media Manager", ["marketing", "ads"]) is False
    assert is_dev_role("Business Development Director", ["sales"]) is False
    assert is_dev_role("UX UI Designer", ["figma", "design"]) is False

def test_is_dev_role_blocks_test_postings():
    assert is_dev_role("TEST JOB", ["test"]) is False
    assert is_dev_role("[Test] Demo Position", ["demo"]) is False
    assert is_dev_role("Sample Developer Role", ["sample"]) is False

def test_is_dev_role_allows_technical_managers():
    # Exception: technical program managers are okay
    assert is_dev_role("Technical Program Manager", ["engineering", "agile"]) is True
    assert is_dev_role("Engineering Manager", ["leadership", "python"]) is True

def test_passes_filters_location():
    cfg = {
        "filters": {
            "locations": ["remote", "united states", "united kingdom"],
            "exclude": ["intern", "contract"]
        }
    }
    job_remote = {"title": "Python Engineer", "location": "Remote", "tags": ["python"]}
    job_us = {"title": "Java Developer", "location": "United States", "tags": ["java"]}
    job_invalid = {"title": "Go Engineer", "location": "Germany", "tags": ["go"]}
    
    assert passes_filters(job_remote, cfg) is True
    assert passes_filters(job_us, cfg) is True
    assert passes_filters(job_invalid, cfg) is False  # Location not in allowed list