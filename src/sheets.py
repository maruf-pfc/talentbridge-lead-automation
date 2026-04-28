import gspread
from google.oauth2.service_account import Credentials
import logging
import os
from src.utils import get_est

# Column headers per Rachel's spec + Location Unverified flag
LEAD_COLS = [
    "Company", "Industry", "Job Title", "Location", 
    "Job URL", "Date Posted", "Date Added", "Location Unverified"
]
DUP_COLS = ["Company", "Title", "URL", "Skipped On"]

def get_sheets_client() -> gspread.Client:
    """Authenticate with Google Sheets using service account."""
    creds_path = os.getenv("GOOGLE_CREDS_PATH", "credentials.json")
    
    if not os.path.exists(creds_path):
        creds_json = os.getenv("GOOGLE_CREDS_JSON")
        if creds_json:
            with open(creds_path, "w", encoding="utf-8") as f:
                f.write(creds_json)
        else:
            raise FileNotFoundError(
                "Missing Google credentials. Set GOOGLE_CREDS_PATH or GOOGLE_CREDS_JSON env var."
            )
    
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    return gspread.authorize(
        Credentials.from_service_account_file(creds_path, scopes=scope)
    )

def push_to_sheets(jobs: list, cfg: dict) -> tuple[int, int]:
    """Append new jobs to Google Sheets, log duplicates."""
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(cfg["sheet_id"])
    except Exception as e:
        logging.error(f"Sheets connection failed: {e}")
        return 0, 0

    # Get or create tabs with exact headers
    for tab_name, headers in [(cfg["leads_tab"], LEAD_COLS), (cfg["duplicates_tab"], DUP_COLS)]:
        try:
            ws = sheet.worksheet(tab_name)
        except gspread.WorksheetNotFound:
            ws = sheet.add_worksheet(tab_name, rows=1000, cols=12)
            ws.append_row(headers)

    leads_ws = sheet.worksheet(cfg["leads_tab"])
    dup_ws = sheet.worksheet(cfg["duplicates_tab"])

    # Load existing leads for dedup (URL-based key per Rachel's fix)
    existing = leads_ws.get_all_values()
    if existing and existing[0][:len(LEAD_COLS)] == LEAD_COLS:
        existing = existing[1:]
    
    seen = {
        (r[0].lower().strip(), r[2].lower().strip(), r[4].lower().strip())
        for r in existing if len(r) >= 5
    }

    new_rows, dup_rows, added, skipped = [], [], 0, 0
    
    for job in jobs:
        # URL-based dedup key (Rachel's fix)
        key = (
            job["company"].lower().strip(),
            job["title"].lower().strip(),
            job["url"].lower().strip()
        )
        
        # Build row with Location Unverified flag
        location_unverified = "Yes" if job.get("location_unverified", False) else "No"
        row = [
            job["company"],
            job["industry"],
            job["title"],
            job["location"],
            job["url"],
            job["date_posted"],
            get_est(),
            location_unverified
        ]
        
        if key in seen:
            dup_rows.append([job["company"], job["title"], job["url"], get_est()])
            skipped += 1
        else:
            new_rows.append(row)
            seen.add(key)
            added += 1

    if new_rows:
        leads_ws.append_rows(new_rows, value_input_option="USER_ENTERED")
        logging.info(f"Appended {len(new_rows)} new leads")
    
    if dup_rows:
        dup_ws.append_rows(dup_rows, value_input_option="USER_ENTERED")
        logging.info(f"Logged {len(dup_rows)} duplicates")

    return added, skipped