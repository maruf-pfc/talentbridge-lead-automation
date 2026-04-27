import requests
import logging
from src.utils import get_est

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_remoteok_jobs(cfg: dict) -> list:
    """Fetch jobs from RemoteOK public API."""
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
    for item in data:
        job = {
            "company": item.get("company", "Unknown"),
            "industry": "Tech/Software",
            "title": item.get("position", "Unknown"),
            "location": item.get("location", "Unknown"),
            "url": item.get("url", ""),
            "date_posted": item.get("date_posted", get_est().split()[0]),
            "tags": item.get("tags", [])  # Critical for filtering
        }
        jobs.append(job)
        if len(jobs) >= 50:  # Fetch enough to filter down to 15+
            break
    
    logging.info(f"RemoteOK: fetched {len(jobs)} raw jobs")
    return jobs

def fetch_all_jobs(cfg: dict) -> list:
    """Aggregate from all sources (currently just RemoteOK)."""
    return fetch_remoteok_jobs(cfg)