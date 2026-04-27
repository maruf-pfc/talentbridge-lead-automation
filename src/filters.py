import re
import logging

def normalize(text: str) -> str:
    """Lowercase, strip emojis/punctuation."""
    if not text: return ""
    text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]', '', str(text))
    return re.sub(r'[^\w\s]', '', text.lower().strip())

def is_dev_role(title: str, tags: list) -> bool:
    text = f"{title} {' '.join(tags)}".lower()
    
    # BLOCK test/demo postings immediately
    if any(x in text for x in ["test job", "demo", "sample", "placeholder", "[test]", "test posting"]):
        return False
    
    # MUST have core dev keyword
    dev_keywords = ["developer", "engineer", "dev ", "software", "backend", "frontend", "fullstack", "python", "javascript", "react", "node", "java", "go", "rust", "ruby", "devops", "sre", "ml engineer", "data engineer"]
    if not any(kw in text for kw in dev_keywords):
        return False
    
    # BLOCK non-dev titles UNLESS they contain "engineer" or "developer"
    block_terms = ["director", "vp", "head of", "manager", "sales", "marketing", "support", "customer success", "business development", "paid media", "medical", "clinical", "ux ", "ui ", "designer", "operations", "strategy", "recruiter", "hr", "finance", "legal"]
    if any(term in text for term in block_terms):
        # Exception: "Technical Program Manager", "Engineering Manager" are okay
        if not any(allow in text for allow in ["engineer", "developer", "technical program", "engineering manager"]):
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