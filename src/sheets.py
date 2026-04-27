import gspread
from google.oauth2.service_account import Credentials
import logging
import os
from src.utils import get_est_time

LEAD_COLS = ["Company", "Industry", "Job Title", "Location", "Job URL", "Date Posted", "Date Added"]
DUP_COLS = ["Company", "Title", "URL", "Skipped On"]

def get_sheets_client() -> gspread.Client:
    creds_path = os.getenv("GOOGLE_CREDS_PATH", "credentials.json")
    if not os.path.exists(creds_path):
        creds_json = os.getenv("GOOGLE_CREDS_JSON")
        if creds_json:
            with open(creds_path, "w", encoding="utf-8") as f: f.write(creds_json)
        else:
            raise FileNotFoundError("Missing Google credentials. Set GOOGLE_CREDS_PATH or GOOGLE_CREDS_JSON env var.")

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    return gspread.authorize(Credentials.from_service_account_file(creds_path, scopes=scope))

def push_to_sheets(jobs: list, cfg: dict) -> tuple:
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(cfg["sheet_id"])
    except Exception as e:
        logging.error(f"Failed to connect to Google Sheets: {e}")
        return 0, 0

    try: leads_ws = sheet.worksheet(cfg["leads_tab"])
    except gspread.WorksheetNotFound:
        leads_ws = sheet.add_worksheet(cfg["leads_tab"], rows=1000, cols=10)
        leads_ws.append_row(LEAD_COLS)

    try: dup_ws = sheet.worksheet(cfg["duplicates_tab"])
    except gspread.WorksheetNotFound:
        dup_ws = sheet.add_worksheet(cfg["duplicates_tab"], rows=1000, cols=10)
        dup_ws.append_row(DUP_COLS)

    existing = leads_ws.get_all_values()
    if existing and existing[0] == LEAD_COLS: existing = existing[1:]

    seen = {(r[0].lower().strip(), r[2].lower().strip(), r[3].lower().strip()) for r in existing if len(r) >= 4}
    new_rows, dup_rows, added, skipped = [], [], 0, 0

    for job in jobs:
        key = (job["company"].lower(), job["title"].lower(), job["location"].lower())
        row = [job["company"], job["industry"], job["title"], job["location"], job["url"], job["date_posted"], get_est_time()]
        if key in seen:
            dup_rows.append([job["company"], job["title"], job["url"], get_est_time()])
            skipped += 1
        else:
            new_rows.append(row)
            seen.add(key)
            added += 1

    if new_rows:
        leads_ws.append_rows(new_rows, value_input_option="USER_ENTERED")
        logging.info(f"Appended {len(new_rows)} new leads to '{cfg['leads_tab']}'")
    if dup_rows:
        dup_ws.append_rows(dup_rows, value_input_option="USER_ENTERED")
        logging.info(f"Logged {len(dup_rows)} duplicates to '{cfg['duplicates_tab']}'")

    return added, skipped