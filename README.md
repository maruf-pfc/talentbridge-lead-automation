# TalentBridge Lead Automation

Automated Python scraper that fetches **developer-only job leads** from RemoteOK and pushes them to your Google Sheet. Built for Rachel Kim @ TalentBridge.

## Features

- **Dev-role filtering**: Only "Engineer", "Developer", or "Dev" titles pass through
- **Block test/demo posts**: Filters out "[TEST]", "Demo Job", "Sample Posting", etc.
- **Location normalization**: Standardizes "Remote", "United States", "United Kingdom"
- **URL-based dedup**: Prevents duplicates even if location strings vary
- **Google Sheets integration**: Append-only, exact column order, EST timestamps
- **Duplicates Log**: Separate tab tracks skipped entries with timestamps
- **Scheduled runs**: GitHub Actions cron at 9 AM EST daily
- **Manual run**: One-command execution for ad-hoc updates
- **Zero paid APIs**: Uses RemoteOK's public JSON API
- **Config-driven filters**: Edit `config.json` to adjust keywords/locations without code changes

## Quick Start

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

## Scheduled Runs (GitHub Actions)

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

## Configuration (`config.json`)

Edit filters without touching code:

```json
{
  "sheet_id": "YOUR_SHEET_ID",
  "leads_tab": "Leads",
  "duplicates_tab": "Duplicates Log",
  "filters": {
    "keywords": ["developer", "engineer", "software", "backend", "frontend"],
    "locations": ["remote", "united states", "us", "united kingdom", "uk"],
    "exclude": ["intern", "contract", "sales", "marketing", "medical"]
  },
  "logging": { "level": "INFO", "file": "run.log" },
  "scraping": { "delay_seconds": 1, "max_retries": 1, "timeout_seconds": 15 }
}
```

### Filter Logic

- **keywords**: Job must contain at least ONE of these in title or tags
- **locations**: Accept jobs with these location strings (plus "Remote"/"Worldwide")
- **exclude**: Block jobs containing any of these terms

## Sheet Structure

### Tab: `Leads` (exact column order)

| A       | B        | C         | D        | E       | F           | G          |
| ------- | -------- | --------- | -------- | ------- | ----------- | ---------- |
| Company | Industry | Job Title | Location | Job URL | Date Posted | Date Added |

### Tab: `Duplicates Log`

| A       | B     | C   | D          |
| ------- | ----- | --- | ---------- |
| Company | Title | URL | Skipped On |

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

## Security Notes

- Never commit `credentials.json` to version control (already in `.gitignore`)
- Use GitHub Secrets for CI/CD credentials
- Rotate service account keys periodically via Google Cloud Console

## Development

### Project Structure

```txt
talentbridge-lead-automation/
├── .github/workflows/schedule.yaml  # GitHub Actions cron
├── src/
│   ├── __init__.py
│   ├── config.py    # Config loader
│   ├── filters.py   # Dev-role filtering logic
│   ├── scraper.py   # RemoteOK API fetcher
│   ├── sheets.py    # Google Sheets handler
│   └── utils.py     # Logging, time, helpers
├── config.json      # Editable filters
├── main.py          # Entry point
├── requirements.txt # Python dependencies
├── run.sh / run.bat # Runner scripts
├── README.md        # This file
└── .gitignore       # Excludes credentials, logs, etc.
```

### Run Tests (Optional)

```bash
# Install test dependencies
pip3 install pytest

# Run unit tests
pytest tests/
```

## Support & Warranty

- **30-day structural fix warranty**: If RemoteOK changes their API format, I'll patch the scraper free within 30 days of delivery
- **Monitoring**: First 3 scheduled runs are monitored silently for failures
- **Contact**: Reply to this repo or email [mmsmaruf.official.com] for urgent issues

_Built for TalentBridge — Delivering quality leads, automatically._
