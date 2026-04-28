import requests
import logging
from bs4 import BeautifulSoup
import re
import time
from src.utils import get_est

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_remoteok_jobs(cfg: dict) -> list:
    """Fetch from RemoteOK public API."""
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
    for item in data[:200]:
        title = item.get("position", "")
        
        # Block test/demo postings
        if any(x in title.lower() for x in ["test job", "demo", "sample"]):
            continue
        
        jobs.append({
            "company": item.get("company", "Unknown"),
            "industry": "Tech/Software",
            "title": str(title).strip(),
            "location": str(item.get("location", "")).strip(),
            "url": str(item.get("url", "")).strip(),
            "date_posted": item.get("date_posted", get_est().split()[0]),
            "tags": item.get("tags", [])
        })
    
    logging.info(f"RemoteOK: {len(jobs)} raw jobs")
    return jobs

def fetch_himalayas_jobs(cfg: dict) -> list:
    """Scrape Himalayas.app HTML — remote-only dev jobs."""
    url = "https://himalayas.app/jobs?remote=true&category=software"
    logging.info("Fetching Himalayas.app...")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        logging.error(f"Himalayas fetch failed: {e}")
        return []
    
    jobs = []
    # Himalayas uses <article class="JobCard"> for job listings
    cards = soup.select("article.JobCard, div[data-job-id], .job-card")
    
    # Fallback: find job links if cards not found
    if not cards:
        job_links = soup.find_all("a", href=re.compile(r"^/jobs/"))
        cards = [link.parent for link in job_links if link.parent and link.parent.name != "body"][:50]
    
    for card in cards[:50]:
        try:
            link = card.find("a", href=re.compile(r"^/jobs/")) or card.find("a")
            if not link:
                continue
            
            # Extract title with cleanup
            title_el = (card.select_one(".JobCard__title") or 
                       card.select_one("h3") or 
                       card.select_one("h4") or 
                       link.select_one("strong") or 
                       link)
            title = title_el.get_text(strip=True) if title_el else ""
            if not title or len(title) < 3:
                continue
            
            # Clean title: remove common job board artifacts
            title = re.sub(r'\s+\d+[a-z]?\s*$', '', title, flags=re.I)  # Remove "AS233", "12d", etc.
            title = re.sub(r'\s*\(Remote\)\s*$', '', title, flags=re.I)  # Remove "(Remote)" suffix
            
            # Extract company
            company_el = (card.select_one(".JobCard__company") or 
                         card.select_one(".company") or 
                         link.select_one("span:first-child"))
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            
            # Extract location
            location_el = card.select_one(".JobCard__location") or card.select_one(".location")
            location = location_el.get_text(strip=True) if location_el else ""
            
            # Build URL
            href = link.get("href", "")
            job_url = f"https://himalayas.app{href}" if href and href.startswith("/") else href
            
            if title and company != "Unknown":
                jobs.append({
                    "company": company,
                    "industry": "Tech/Software",
                    "title": title,
                    "location": location if location else "",
                    "url": job_url,
                    "date_posted": get_est().split()[0],
                    "tags": []
                })
        except Exception as e:
            logging.debug(f"Himalayas parse error: {e}")
            continue
    
    time.sleep(1.0)  # Polite rate limit
    logging.info(f"Himalayas: {len(jobs)} raw jobs")
    return jobs

def fetch_all_jobs(cfg: dict) -> list:
    """Aggregate from all sources."""
    all_jobs = fetch_remoteok_jobs(cfg)
    all_jobs.extend(fetch_himalayas_jobs(cfg))
    logging.info(f"Total raw jobs fetched: {len(all_jobs)}")
    return all_jobs