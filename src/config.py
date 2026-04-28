import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_config(path: str = "config.json") -> Dict[str, Any]:
    """Load and validate configuration from JSON file."""
    config_path = Path(path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {path}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")
    
    # Validate required fields
    required = ["sheet_id", "leads_tab", "duplicates_tab"]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {missing}")
    
    logger.info(f"Loaded config from {path}")
    return config