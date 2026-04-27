import logging
import time
from datetime import datetime
import pytz

def setup_logging(cfg: dict):
    logging.basicConfig(
        level=cfg["logging"].get("level", "INFO").upper(),
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(cfg["logging"].get("file", "run.log"), mode="a", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def get_est_time() -> str:
    return datetime.now(pytz.timezone("America/New_York")).strftime("%Y-%m-%d %H:%M:%S EST")

def safe_request(request_func, max_retries: int, *args, **kwargs):
    attempts = 0
    while attempts <= max_retries:
        try:
            response = request_func(*args, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            attempts += 1
            if attempts > max_retries:
                logging.warning(f"Request failed after {max_retries} retries: {e}")
                return None
            time.sleep(2)