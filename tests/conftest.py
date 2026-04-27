import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_config():
    return {
        "filters": {
            "keywords": ["developer", "engineer"],
            "locations": ["remote", "united states", "united kingdom"],
            "exclude": ["intern", "contract", "sales"]
        }
    }