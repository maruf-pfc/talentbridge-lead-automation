import requests
import logging
import re
from src.utils import get_est

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def _is_test_posting(title: str, company: str) -> bool:
    """Block test/demo/sample postings that pollute lead quality."""
    text = f"{title} {company}".lower()
    test_indicators = [
        "test job", "test posting", "[test]", "demo", "sample", "placeholder",
        "example job", "do not apply", "internal test", "qa test", "debug"
    ]
    return any(indicator in text for indicator in test_indicators)

def _is_clearly_non_dev(title: str, tags: list) -> bool:
    """Early-exclude roles that are definitely not developer positions."""
    text = f"{title} {' '.join(tags)}".lower()
    
    # Hard-block these categories entirely
    hard_blocks = [
        "medical director", "clinical director", "physician", "doctor", "nurse",
        "paid media", "growth marketer", "seo specialist", "content writer", "copywriter",
        "business development", "sales representative", "account executive", "sdr", "bdr",
        "customer success", "support specialist", "help desk", "recruiter", "hr ", "human resources",
        "finance manager", "legal counsel", "paralegal", "operations manager", "strategy ",
        "ux designer", "ui designer", "graphic designer", "product designer" if "engineer" not in text else "",
        "project manager" if "technical" not in text and "engineer" not in text else "",
    ]
    
    return any(block in text for block in hard_blocks if block)

def _normalize_location(location: str) -> str:
    """Normalize location strings for consistent filtering."""
    if not location:
        return "Unknown"
    loc = location.lower().strip()
    # Standardize remote variants
    if any(x in loc for x in ["worldwide", "remote", "anywhere", "global", "🌍", "work from anywhere"]):
        return "Remote"
    # Keep country names clean
    if "united states" in loc or "usa" in loc or "us " in loc or loc == "us":
        return "United States"
    if "united kingdom" in loc or "uk " in loc or loc == "uk":
        return "United Kingdom"
    return location.strip()

def fetch_remoteok_jobs(cfg: dict) -> list:
    """Fetch jobs from RemoteOK public API with pre-filtering."""
    url = "https://remoteok.io/api"
    logging.info("Fetching RemoteOK...")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        logging.error(f"RemoteOK fetch failed: {e}")
        return []
    
    jobs = []
    skipped_test = 0
    skipped_non_dev = 0
    
    for item in data:
        title = item.get("position", "")
        company = item.get("company", "Unknown")
        tags = item.get("tags", [])
        location_raw = item.get("location", "")
        url_job = item.get("url", "")
        
        # 1. Block test/demo postings immediately
        if _is_test_posting(title, company):
            skipped_test += 1
            logging.debug(f"Skipped TEST posting: {company} — {title}")
            continue
        
        # 2. Early-exclude clearly non-dev roles (before building full job dict)
        if _is_clearly_non_dev(title, tags):
            skipped_non_dev += 1
            logging.debug(f"Skipped non-dev role: {company} — {title}")
            continue
        
        # 3. Build clean job dict with normalized location
        job = {
            "company": company.strip(),
            "industry": "Tech/Software",
            "title": title.strip(),
            "location": _normalize_location(location_raw),
            "url": url_job.strip(),
            "date_posted": item.get("date_posted", get_est().split()[0]),
            "tags": [str(t).strip() for t in tags]  # Ensure tags are clean strings
        }
        
        # 4. Require URL for dedup integrity
        if not job["url"]:
            logging.debug(f"Skipped job with missing URL: {company} — {title}")
            continue
        
        jobs.append(job)
        
        # Fetch enough to ensure 15+ survive final filtering
        if len(jobs) >= 60:
            break
    
    logging.info(f"RemoteOK: fetched {len(jobs)} jobs after pre-filtering (skipped {skipped_test} test, {skipped_non_dev} non-dev)")
    return jobs

def fetch_all_jobs(cfg: dict) -> list:
    """Aggregate from all sources (currently just RemoteOK)."""
    return fetch_remoteok_jobs(cfg)