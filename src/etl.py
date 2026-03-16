"""
ETL pipeline: loads raw scraped JSON, cleans and normalises the data,
and writes a processed CSV + JSON ready for analysis.
"""

import json
import os
import re
import logging
from glob import glob

import pandas as pd
import numpy as np

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)


def _latest_raw_file() -> str:
    """Return the most-recently created raw JSON file."""
    files = sorted(glob(os.path.join(RAW_DATA_DIR, "indiamart_raw_*.json")))
    if not files:
        raise FileNotFoundError(f"No raw data files found in {RAW_DATA_DIR}")
    return files[-1]


def _parse_price(val: str | None) -> float | None:
    if not val:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _normalise_location(loc: str) -> dict[str, str]:
    """
    Best-effort split of 'City, State' or 'City State' strings.
    IndiaMART locations are inconsistent, so we do our best.
    """
    if not loc:
        return {"city": "", "state": ""}

    parts = re.split(r"[,|]+", loc)
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) >= 2:
        return {"city": parts[0], "state": parts[-1]}
    return {"city": parts[0] if parts else "", "state": ""}


def load_raw(path: str | None = None) -> pd.DataFrame:
    """Load raw JSON into a DataFrame."""
    path = path or _latest_raw_file()
    logger.info("Loading raw data from %s", path)

    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)

    df = pd.DataFrame(payload["data"])
    logger.info("Loaded %d raw records", len(df))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning and normalisation transformations."""
    df = df.copy()

    df.drop_duplicates(subset=["product_name", "supplier_name", "product_url"], inplace=True)

    df["price_min"] = df["price_min"].apply(_parse_price)
    df["price_max"] = df["price_max"].apply(_parse_price)

    loc_parts = df["location"].apply(_normalise_location).apply(pd.Series)
    df["city"] = loc_parts["city"]
    df["state"] = loc_parts["state"]

    df["product_name"] = df["product_name"].str.strip()
    df["supplier_name"] = df["supplier_name"].str.strip()
    df["description"] = df["description"].str.strip()

    df["has_price"] = df["price_min"].notna()
    df["has_location"] = df["location"].astype(bool)

    df.reset_index(drop=True, inplace=True)
    logger.info("After cleaning: %d records", len(df))
    return df


def save_processed(df: pd.DataFrame) -> tuple[str, str]:
    """Write cleaned data to CSV and JSON."""
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    csv_path = os.path.join(PROCESSED_DATA_DIR, "indiamart_cleaned.csv")
    json_path = os.path.join(PROCESSED_DATA_DIR, "indiamart_cleaned.json")

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    logger.info("Saved processed data -> %s, %s", csv_path, json_path)
    return csv_path, json_path


def run_etl(raw_path: str | None = None) -> pd.DataFrame:
    """Full ETL pipeline: load → clean → save. Returns the cleaned DataFrame."""
    df_raw = load_raw(raw_path)
    df_clean = clean(df_raw)
    csv_path, json_path = save_processed(df_clean)

    print(f"\n{'='*60}")
    print("  ETL Pipeline - Complete")
    print(f"  Raw records   : {len(df_raw)}")
    print(f"  Clean records : {len(df_clean)}")
    print(f"  CSV  output   : {csv_path}")
    print(f"  JSON output   : {json_path}")
    print(f"{'='*60}\n")

    return df_clean
