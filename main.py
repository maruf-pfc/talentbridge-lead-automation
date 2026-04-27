import logging
from src.config import load_config
from src.scraper import fetch_all_jobs
from src.filters import passes_filters
from src.sheets import push_to_sheets
from src.utils import setup_logging

def main():
    cfg = load_config()
    setup_logging(cfg)
    logger = logging.getLogger(__name__)

    logger.info("--- Starting TalentBridge Scraper ---")
    raw_jobs = fetch_all_jobs(cfg)
    logger.info(f"Raw jobs fetched: {len(raw_jobs)}")

    filtered = [j for j in raw_jobs if passes_filters(j, cfg)]
    logger.info(f"Passed filters: {len(filtered)}")

    added, skipped = push_to_sheets(filtered, cfg)
    logger.info(f"FINAL STATS | Found: {len(filtered)} | Added: {added} | Duplicates: {skipped}")
    logger.info("--- Scraper Finished ---")

if __name__ == "__main__":
    main()