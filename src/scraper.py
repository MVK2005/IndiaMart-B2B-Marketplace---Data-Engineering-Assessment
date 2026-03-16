"""
Orchestrator that drives the crawl across categories and pages,
delegates parsing, and persists raw results.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from tqdm import tqdm

from src.config import (
    CATEGORIES,
    INDIAMART_SEARCH_URL,
    MAX_PAGES_PER_CATEGORY,
    RAW_DATA_DIR,
)
from src.http_client import ResilientClient
from src.parser import parse_search_page

logger = logging.getLogger(__name__)


def _build_url(query: str, page: int) -> str:
    return INDIAMART_SEARCH_URL.format(query=query.replace(" ", "+"), page=page)


def scrape_category(
    client: ResilientClient,
    category_key: str,
    meta: dict,
    max_pages: int = MAX_PAGES_PER_CATEGORY,
) -> list[dict[str, Any]]:
    """Scrape all pages for a single category and return product records."""
    all_records: list[dict[str, Any]] = []

    for page in tqdm(range(1, max_pages + 1), desc=f"  {category_key}", unit="pg"):
        url = _build_url(meta["search_query"], page)
        resp = client.get(url)
        if resp is None:
            logger.warning("Skipping page %d of %s (no response)", page, category_key)
            continue

        records = parse_search_page(resp.text, category_key)
        if not records:
            logger.info("No more results on page %d for %s — stopping early", page, category_key)
            break

        all_records.extend(records)

    logger.info("Category '%s': collected %d records", category_key, len(all_records))
    return all_records


def run_scraper(
    categories: dict | None = None,
    max_pages: int = MAX_PAGES_PER_CATEGORY,
) -> str:
    """
    Main entry-point.  Scrapes all configured categories and writes
    a timestamped JSON file into data/raw/.

    Returns the path to the output file.
    """
    categories = categories or CATEGORIES
    client = ResilientClient()
    all_data: list[dict[str, Any]] = []

    print(f"\n{'='*60}")
    print("  IndiaMART Scraper - Starting crawl")
    print(f"  Categories : {list(categories.keys())}")
    print(f"  Max pages  : {max_pages} per category")
    print(f"{'='*60}\n")

    try:
        for cat_key, cat_meta in categories.items():
            records = scrape_category(client, cat_key, cat_meta, max_pages)
            all_data.extend(records)
    finally:
        client.close()

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(RAW_DATA_DIR, f"indiamart_raw_{ts}.json")

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "scraped_at": ts,
                "total_records": len(all_data),
                "categories": list(categories.keys()),
                "data": all_data,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n[OK] Saved {len(all_data)} records -> {out_path}")
    return out_path
