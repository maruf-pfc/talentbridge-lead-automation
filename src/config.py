import json
from pathlib import Path

def load_config(path: str = "config.json") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)