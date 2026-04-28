import re
import logging

def normalize(text: str) -> str:
    """Lowercase, strip punctuation/emojis, collapse spaces."""
    if not text:
        return ""
    # Remove emojis and special characters
    text = re.sub(r'[^\w\s]', '', str(text).lower().strip())
    return re.sub(r'\s+', ' ', text)

# TITLE WHITELIST: Must contain at least ONE of these (Rachel's spec)
DEV_TERMS = [
    "engineer", "developer", "software", "frontend", "backend", "fullstack", "full-stack",
    "devops", "sre", "architect", "ml ", "machine learning", "data engineer",
    "python ", "javascript", "react", "node", "go ", "golang", "rust", "ruby", "java",
    "cloud engineer", "security engineer", "platform engineer", "solutions architect",
    "product engineer", "staff engineer", "principal engineer"
]

# STRICT BLOCKLIST: Zero tolerance for non-dev roles
BLOCK_TERMS = [
    "intern", "contract", "freelance", "sales", "marketing", "support", "customer success",
    "medical", "clinical", "ux ", "ui ", "designer", "business development", "operations manager",
    "account executive", "sdr", "bdr", "recruiter", "hr ", "finance", "legal", "copywriter",
    "paid media", "growth marketer", "content writer", "writer", "editor"
]

# LOCATION PASS-LIST: Simple substring match per Rachel's spec
PASS_LOCATIONS = [
    "remote", "us", "usa", "united states", "canada", "uk", "united kingdom", "north america"
]

def is_dev_role(title: str) -> bool:
    """Return True if title contains a dev term AND no block terms."""
    t = title.lower()
    
    # Must have at least one dev keyword
    if not any(term in t for term in DEV_TERMS):
        return False
    
    # Must not have any block terms
    if any(block in t for block in BLOCK_TERMS):
        return False
    
    return True

def check_location(location: str) -> tuple[bool, bool]:
    """
    Returns (is_valid, is_unverified) per Rachel's spec:
    - If location contains any PASS_LOCATIONS substring → valid, not unverified
    - If location is empty/unknown → valid BUT unverified (flag for sheet)
    - Everything else → invalid (block)
    """
    if not location or normalize(location) in ["unknown", "n/a", ""]:
        return True, True  # Pass but flag as unverified
    
    loc = normalize(location)
    is_valid = any(target in loc for target in PASS_LOCATIONS)
    return is_valid, False

def passes_filters(job: dict, cfg: dict) -> tuple[bool, bool]:
    """
    Returns (should_include, is_location_unverified)
    """
    title = job.get("title", "")
    location = job.get("location", "")
    
    # Block test/demo postings immediately
    if any(x in title.lower() for x in ["test job", "demo", "sample", "[test]", "placeholder"]):
        return False, False
    
    # Must be a dev role
    if not is_dev_role(title):
        return False, False
    
    # Check location
    is_valid, is_unverified = check_location(location)
    if not is_valid:
        return False, False
    
    return True, is_unverified