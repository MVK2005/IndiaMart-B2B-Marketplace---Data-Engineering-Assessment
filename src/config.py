"""
Central configuration for the IndiaMART scraper.
All tuneable parameters live here so the rest of the codebase stays clean.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

CATEGORIES = {
    "industrial-machinery": {
        "search_query": "industrial machinery",
        "url_slug": "industrial-machinery",
    },
    "electronics-components": {
        "search_query": "electronic components",
        "url_slug": "electronic-components",
    },
    "textiles-fabrics": {
        "search_query": "textiles fabrics",
        "url_slug": "textiles-fabrics",
    },
}

INDIAMART_SEARCH_URL = "https://dir.indiamart.com/search.mp?ss={query}&prdsrc=1&mcatid=&catid=&pgno={page}"

REQUEST_DELAY_RANGE = (2, 5)       # seconds between requests (randomised)
MAX_PAGES_PER_CATEGORY = 10        # pages of search results to crawl
MAX_RETRIES = 3
RETRY_BACKOFF = 5                  # seconds base backoff on 429 / 5xx

REQUEST_TIMEOUT = 20               # seconds

# Rotating headers to reduce fingerprinting
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
