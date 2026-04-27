import re

def normalize(text: str) -> str:
    return re.sub(r'[^\w\s]', '', str(text).lower().strip())

def passes_filters(job: dict, cfg: dict) -> bool:
    title = normalize(job.get("title", ""))
    location = normalize(job.get("location", ""))
    text = f"{title} {location}"

    keywords = [k.lower() for k in cfg["filters"]["keywords"]]
    exclude = [e.lower() for e in cfg["filters"]["exclude"]]
    locations = [l.lower() for l in cfg["filters"]["locations"]]

    has_keyword = any(kw in text for kw in keywords)
    not_excluded = not any(ex in text for ex in exclude)
    has_location = any(loc in text for loc in locations)

    return has_keyword and not_excluded and has_location