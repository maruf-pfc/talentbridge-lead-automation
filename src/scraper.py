import requests
from bs4 import BeautifulSoup
import logging
import time
from src.utils import safe_request, get_est_time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def fetch_wwr_jobs(cfg: dict) -> list:
    url = "https://weworkremotely.com/categories/remote-programming-jobs"
    logging.info("Fetching We Work Remotely...")
    res = safe_request(requests.get, cfg["scraping"]["max_retries"], url, headers=HEADERS, timeout=cfg["scraping"]["timeout_seconds"])
    if not res: return []

    soup = BeautifulSoup(res.text, "html.parser")
    jobs = []
    for item in soup.select("li.featured-list"):
        try:
            title = item.select_one("span.title")
            company = item.select_one("span.company")
            link = item.select_one("a")

            jobs.append({
                "company": company.get_text(strip=True) if company else "Unknown",
                "industry": "Tech/Software",
                "title": title.get_text(strip=True) if title else "Unknown",
                "location": "Remote",
                "url": f"https://weworkremotely.com{link['href']}" if link else "",
                "date_posted": get_est_time().split(" ")[0]
            })
        except Exception as e:
            logging.warning(f"Error parsing WWR job: {e}")
    time.sleep(cfg["scraping"]["delay_seconds"])
    return jobs

def fetch_wellfound_jobs(cfg: dict) -> list:
    url = "https://wellfound.com/roles/jobs"
    logging.info("Fetching Wellfound...")
    res = safe_request(requests.get, cfg["scraping"]["max_retries"], url, headers=HEADERS, timeout=cfg["scraping"]["timeout_seconds"])
    if not res: return []

    soup = BeautifulSoup(res.text, "html.parser")
    jobs = []
    # Wellfound structure changes frequently. We target common card containers with fallback.
    cards = soup.select("div[class*='JobCard'], li[class*='job'], a[class*='job']")[:30]
    if not cards:
        cards = soup.select("a[href*='/roles']")[:20]

    for card in cards:
        try:
            title = card.select_one("span, h3, div[class*='title']")
            company = card.select_one("span[class*='company'], div[class*='company']")
            location = card.select_one("span[class*='location'], div[class*='location']")
            link_tag = card if card.name == "a" else card.find_parent("a")

            title_txt = title.get_text(strip=True) if title else ""
            if not title_txt: continue

            link = link_tag["href"] if link_tag and "href" in link_tag.attrs else "https://wellfound.com/roles/jobs"
            if link.startswith("/"): link = f"https://wellfound.com{link}"

            jobs.append({
                "company": company.get_text(strip=True) if company else "Unknown",
                "industry": "Tech/Software",
                "title": title_txt,
                "location": location.get_text(strip=True) if location else "Remote",
                "url": link,
                "date_posted": get_est_time().split(" ")[0]
            })
        except Exception as e:
            logging.warning(f"Error parsing Wellfound job: {e}")
    time.sleep(cfg["scraping"]["delay_seconds"])
    return jobs

def fetch_all_jobs(cfg: dict) -> list:
    all_jobs = []
    all_jobs.extend(fetch_wwr_jobs(cfg))
    all_jobs.extend(fetch_wellfound_jobs(cfg))
    logging.info(f"Total raw jobs fetched: {len(all_jobs)}")
    return all_jobs