# TalentBridge Lead Automation

Automates the collection of companies actively hiring developers and delivers structured lead data directly into Google Sheets.

## Setup

1. `pip install -r requirements.txt`
2. Create Google Service Account → enable Sheets API → download `credentials.json` → place in project root
3. Share your Google Sheet with the service account email (found in `credentials.json`)
4. Run: `python main.py` or `./run.sh`

## Scheduling (GitHub Actions)

- Push to GitHub
- Add `GOOGLE_CREDS_JSON` as a repository secret (paste entire JSON file contents)
- Workflow triggers daily at 9 AM EST via cron

## Configuration

Edit `config.json` to adjust keywords, locations, or exclusions. No code changes required.
