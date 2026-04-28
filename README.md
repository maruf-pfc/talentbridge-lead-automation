# TalentBridge Lead Scraper 🎯

Automated Python scraper that fetches **developer-only job leads** from RemoteOK and Himalayas.app, then pushes them to your Google Sheet. Built for Rachel Kim @ TalentBridge.

---

## ✅ Features

- **Dev-role filtering**: Only "Engineer", "Developer", "Architect", or "Software" titles pass through
- **Block test/demo posts**: Filters out "[TEST]", "Demo Job", "Sample Posting", etc.
- **Location gate**: Accepts Remote, US, UK, Canada, North America only (configurable)
- **Location Unverified flag**: Empty/unknown locations pass but are flagged for review
- **URL-based dedup**: Prevents duplicates even if location strings vary
- **Google Sheets integration**: Append-only, exact column order, EST timestamps
- **Duplicates Log**: Separate tab tracks skipped entries with timestamps
- **Scheduled runs**: GitHub Actions cron at 9 AM EST daily
- **Manual run**: One-command execution for ad-hoc updates
- **Zero paid APIs**: Uses RemoteOK's public JSON API + Himalayas HTML scraping
- **Config-driven filters**: Edit `src/filters.py` to adjust keywords/locations without code changes

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Cloud project with Sheets API enabled
- Service account credentials (`credentials.json`)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google Sheets Access

1. Create a Google Service Account ([guide](https://gspread.readthedocs.io/en/latest/oauth2.html))
2. Download `credentials.json` and place in project root
3. Share your target Google Sheet with the service account email (found in `credentials.json`) → **Editor** permission
4. Copy your Sheet ID from the URL and update `config.json`:
   ```json
   { "sheet_id": "YOUR_SHEET_ID_HERE" }
   ```

### 3. Run the Scraper

```bash
# Manual run
python3 main.py

# Or use the runner script
./run.sh          # macOS/Linux
run.bat           # Windows
```

### 4. Verify Output

- Check `run.log` for execution stats
- Open your Google Sheet → `Leads` tab should have new rows
- Check `Duplicates Log` tab for skipped entries

---

## ⏰ Scheduled Runs (GitHub Actions)

### Setup

1. Push this repo to GitHub
2. Add repository secret `GOOGLE_CREDS_JSON`:
   - Go to **Settings → Secrets and variables → Actions**
   - New secret: `GOOGLE_CREDS_JSON`
   - Value: Paste the **entire contents** of `credentials.json`
3. The workflow triggers automatically at **9 AM EST daily**

### Cron Timing Note

GitHub Actions cron uses UTC. Our workflow:

```yaml
cron: "0 14 * * *" # 14:00 UTC = 9:00 AM EST / 10:00 AM EDT
env:
  TZ: America/New_York # Ensures logs/timestamps use EST
```

---

## ⚙️ Configuration

### Filters (`src/filters.py`)

Edit these lists to tune filtering without code changes:

```python
DEV_TERMS = ["engineer", "developer", "software", ...]  # Title whitelist
BLOCK_TERMS = ["intern", "sales", "marketing", ...]     # Title blocklist
PASS_LOCATIONS = ["remote", "us", "uk", "canada", ...]  # Location whitelist
```

### Config (`config.json`)

```json
{
  "sheet_id": "YOUR_SHEET_ID",
  "leads_tab": "Leads",
  "duplicates_tab": "Duplicates Log",
  "logging": { "level": "INFO", "file": "run.log" }
}
```

---

## 📊 Sheet Structure

### Tab: `Leads` (exact column order)

| A       | B        | C         | D        | E       | F           | G          | H                   |
| ------- | -------- | --------- | -------- | ------- | ----------- | ---------- | ------------------- |
| Company | Industry | Job Title | Location | Job URL | Date Posted | Date Added | Location Unverified |

### Tab: `Duplicates Log`

| A       | B     | C   | D          |
| ------- | ----- | --- | ---------- |
| Company | Title | URL | Skipped On |

---

## 🐛 Troubleshooting

### "Missing credentials" error

- Ensure `credentials.json` exists in project root OR set env var `GOOGLE_CREDS_JSON`

### "Sheet not found" error

- Verify Sheet ID in `config.json` matches your Google Sheet URL
- Confirm service account has **Editor** access to the sheet

### "0 jobs added" but no errors

- Check `run.log` for filtering decisions
- Temporarily set `"level": "DEBUG"` in `config.json` to see why jobs are filtered

### Cron not triggering

- Verify workflow file is in `.github/workflows/`
- Check GitHub Actions tab for run history
- Ensure `GOOGLE_CREDS_JSON` secret is set correctly

### Himalayas jobs not appearing

- Himalayas jobs often have EU/Asia locations which fail the location gate
- To include them, add `"europe"`, `"germany"`, etc. to `PASS_LOCATIONS` in `src/filters.py`

---

## 🔐 Security Notes

- Never commit `credentials.json` to version control (already in `.gitignore`)
- Use GitHub Secrets for CI/CD credentials
- Rotate service account keys periodically via Google Cloud Console

---

## 🛠️ Development

### Project Structure

```
talentbridge-scraper/
├── .github/workflows/schedule.yaml  # GitHub Actions cron
├── src/
│   ├── __init__.py
│   ├── config.py    # Config loader
│   ├── filters.py   # Dev-role filtering logic
│   ├── scraper.py   # RemoteOK + Himalayas fetchers
│   ├── sheets.py    # Google Sheets handler
│   └── utils.py     # Logging, time, helpers
├── config.json      # Sheet ID + logging config
├── main.py          # Entry point
├── requirements.txt # Python dependencies
├── run.sh / run.bat # Runner scripts
├── README.md        # This file
└── .gitignore       # Excludes credentials, logs, etc.
```

### Run Tests

```bash
# Install test dependencies
pip install pytest

# Run unit tests
pytest tests/ -v
```
