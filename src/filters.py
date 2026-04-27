import re
import logging

def normalize(text: str) -> str:
    """Lowercase, strip emojis/punctuation."""
    if not text: return ""
    text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]', '', str(text))
    return re.sub(r'[^\w\s]', '', text.lower().strip())

def is_dev_role(title: str, tags: list) -> bool:
    """Return True ONLY if role is clearly a developer/engineering position."""
    text = f"{title} {' '.join(tags)}".lower()
    
    # Must contain at least ONE core dev keyword
    dev_keywords = [
        "developer", "engineer", "dev", "software", "backend", "frontend", 
        "fullstack", "full-stack", "python", "javascript", "react", "node", 
        "java", "go", "rust", "ruby", "php", "ios", "android", "mobile dev",
        "web dev", "api developer", "data engineer", "ml engineer", "ai engineer",
        "cloud engineer", "devops", "site reliability", "sre"
    ]
    if not any(kw in text for kw in dev_keywords):
        return False
    
    # Must NOT contain non-dev role indicators
    non_dev_keywords = [
        "manager", "director", "vp", "head of", "lead" in text and "engineer" not in text,
        "sales", "marketing", "support", "customer success", "hr", "recruiter",
        "finance", "legal", "operations" in text and "devops" not in text,
        "business development", "account manager", "project manager" in text and "technical" not in text,
        "ux", "ui", "designer" in text and "engineer" not in text,
        "medical", "clinical", "healthcare" in text and "engineer" not in text,
        "paid media", "growth marketer", "seo", "content", "writer"
    ]
    if any(kw in text for kw in non_dev_keywords if isinstance(kw, str)):
        # Special case: "Technical Project Manager" is okay
        if "technical" in text and ("project manager" in text or "program manager" in text):
            return True
        return False
    
    return True

def passes_filters(job: dict, cfg: dict) -> bool:
    title = job.get("title", "")
    location = job.get("location", "").lower()
    tags = job.get("tags", [])
    
    # 1. Must be a dev role
    if not is_dev_role(title, tags):
        logging.debug(f"Filtered out non-dev role: {title}")
        return False
    
    # 2. Location must be Remote/US/UK
    valid_locations = [normalize(l) for l in cfg["filters"]["locations"]]
    loc_normalized = normalize(location)
    loc_match = any(loc in loc_normalized for loc in valid_locations) or \
                any(x in loc_normalized for x in ["remote", "worldwide", "anywhere", "global", "🌍"])
    
    if not loc_match:
        logging.debug(f"Filtered out by location: {location}")
        return False
    
    # 3. Exclude internships/contracts
    exclude = [normalize(e) for e in cfg["filters"]["exclude"]]
    text = normalize(f"{title} {' '.join(tags)}")
    if any(ex in text for ex in exclude):
        logging.debug(f"Filtered out by exclude list: {title}")
        return False
    
    return True