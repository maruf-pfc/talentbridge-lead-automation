import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_config():
    return {
        "sheet_id": "test-sheet-id",
        "leads_tab": "Leads",
        "duplicates_tab": "Duplicates Log",
        "filters": {
            "locations": ["remote", "us", "uk", "canada"],
            "exclude": ["intern", "contract"]
        }
    }