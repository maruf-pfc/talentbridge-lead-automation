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

    logger.info("=== TalentBridge Scraper ===")
    
    # Fetch jobs from all sources
    raw_jobs = fetch_all_jobs(cfg)
    logger.info(f"Raw jobs fetched: {len(raw_jobs)}")

    # Filter jobs and attach location_unverified flag
    filtered = []
    for job in raw_jobs:
        should_include, is_unverified = passes_filters(job, cfg)
        if should_include:
            job["location_unverified"] = is_unverified
            filtered.append(job)
    
    logger.info(f"Passed filters: {len(filtered)}")

    # Volume guardrail (log warning if <15, but don't pad)
    if len(filtered) < 15:
        logger.warning(f"⚠️ VOLUME ALERT: Only {len(filtered)} clean leads today.")
    else:
        logger.info(f"✅ Target met: {len(filtered)} clean dev leads.")

    # Push to Google Sheets
    added, skipped = push_to_sheets(filtered, cfg)
    
    logger.info(f"FINAL | Found: {len(filtered)} | Added: {added} | Duplicates: {skipped}")
    logger.info("=== Done ===")

if __name__ == "__main__":
    main()