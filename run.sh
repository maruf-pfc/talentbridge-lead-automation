#!/bin/bash
# TalentBridge Lead Automation
# Usage: ./run.sh

set -e  # Exit on error

echo "🚀 Starting TalentBridge Lead Scraper..."
echo "📅 Timestamp: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo ""

# Ensure we're in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3.10+"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ] && [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate 2>/dev/null || true
fi

# Run the scraper
echo "🔍 Fetching leads..."
python3 main.py

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Scraper completed successfully."
    echo "📊 Check run.log for detailed stats."
    echo "📈 Open your Google Sheet to view new leads."
else
    echo "❌ Scraper failed with exit code $EXIT_CODE"
    echo "🔍 Check run.log for error details."
fi

# Deactivate venv if active
deactivate 2>/dev/null || true

exit $EXIT_CODE