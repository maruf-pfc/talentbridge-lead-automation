import logging
import pytz
from datetime import datetime

def setup_logging(cfg: dict):
    logging.basicConfig(
        level=cfg.get("logging", {}).get("level", "INFO").upper(),
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(cfg.get("logging", {}).get("file", "run.log"), mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def get_est() -> str:
    return datetime.now(pytz.timezone("America/New_York")).strftime("%Y-%m-%d %H:%M:%S EST")