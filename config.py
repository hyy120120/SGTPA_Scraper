"""
config.py
Central configuration for the SGTPA scraper.
"""

from pathlib import Path

# ------------------------------------------------------------------
# Project
# ------------------------------------------------------------------

PROJECT_NAME = "SGTPA Scraper"

BASE_URL = "https://www.sgtpa.com"
MEMBERS_URL = BASE_URL + "/members/"

# ------------------------------------------------------------------
# HTTP
# ------------------------------------------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}

REQUEST_TIMEOUT = 30
VERIFY_SSL = True

# ------------------------------------------------------------------
# Retry
# ------------------------------------------------------------------

MAX_RETRIES = 5
BACKOFF_FACTOR = 2

# ------------------------------------------------------------------
# Crawling
# ------------------------------------------------------------------

MAX_WORKERS = 5

MIN_DELAY = 0.4
MAX_DELAY = 1.2

# ------------------------------------------------------------------
# Output
# ------------------------------------------------------------------

ROOT = Path(__file__).parent

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

EXCEL_FILE = OUTPUT_DIR / "SGTPA_Members.xlsx"
CSV_FILE = OUTPUT_DIR / "SGTPA_Members.csv"

URL_CACHE = OUTPUT_DIR / "member_urls.json"

FAILED_URLS = OUTPUT_DIR / "failed_urls.txt"

LOG_FILE = OUTPUT_DIR / "crawler.log"

# ------------------------------------------------------------------
# Resume
# ------------------------------------------------------------------

ENABLE_RESUME = True

PROGRESS_FILE = OUTPUT_DIR / "progress.json"

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

LOG_LEVEL = "INFO"

# ------------------------------------------------------------------
# Export
# ------------------------------------------------------------------

EXPORT_EXCEL = True
EXPORT_CSV = True

REMOVE_DUPLICATES = True

SORT_BY = "Company Name"

# ------------------------------------------------------------------
# Parser
# ------------------------------------------------------------------

EMAIL_REGEX = r"[\\w\\.-]+@[\\w\\.-]+\\.\\w+"

PHONE_REGEX = r"[+]?\\d[\\d\\s\\-()]{6,}"

# ------------------------------------------------------------------
# Developer
# ------------------------------------------------------------------

DEBUG = False
