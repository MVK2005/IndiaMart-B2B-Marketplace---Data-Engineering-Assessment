"""
HTML parser for IndiaMART search result pages.

The parser extracts structured product/supplier records from each search-results page.
"""

import re
import logging
from typing import Any

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


def _clean(text: str | None) -> str:
    """Strip whitespace and collapse internal runs of whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _extract_price(card: Tag) -> dict[str, Any]:
    """Pull price value and unit from a product card."""
    price_el = card.select_one(".prc, .price, [class*='price'], [class*='prc']")
    raw = _clean(price_el.get_text() if price_el else "")

    numbers = re.findall(r"[\d,]+\.?\d*", raw)
    unit_match = re.search(r"/([\w\s]+)", raw)

    return {
        "price_raw": raw,
        "price_min": numbers[0].replace(",", "") if numbers else None,
        "price_max": numbers[1].replace(",", "") if len(numbers) > 1 else None,
        "price_unit": unit_match.group(1).strip() if unit_match else None,
    }


def _extract_location(card: Tag) -> str:
    """Extract supplier city / state from a card."""
    loc_el = card.select_one(
        ".lcn, .location, [class*='clg'], [class*='loc'], .cityNm"
    )
    return _clean(loc_el.get_text() if loc_el else "")


def parse_search_page(html: str, category: str) -> list[dict[str, Any]]:
    """
    Parse a single IndiaMART search-results page and return a list of
    product records.

    Each record contains:
        - product_name
        - supplier_name
        - price_raw / price_min / price_max / price_unit
        - location
        - description
        - product_url
        - category
    """
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("[id^='prodCard']")

    if not cards:
        cards = soup.select(".brs, .lst, [class*='cardCont'], .snp-card, .productsCard")
    if not cards:
        cards = soup.select("div[data-product]")
    if not cards:
        cards = soup.select(".card, .product-card, .listing")

    results: list[dict[str, Any]] = []

    for card in cards:
        name_el = card.select_one(
            ".lcname, .prdnm, [class*='prodName'], a.cardTitle, .product-name, h2, h3"
        )
        product_name = _clean(name_el.get_text() if name_el else "")
        if not product_name:
            continue

        supplier_el = card.select_one(
            ".companyname, .cmpnm, [class*='compName'], .supplier-name, .company"
        )
        supplier_name = _clean(supplier_el.get_text() if supplier_el else "")

        desc_el = card.select_one(
            ".pdesc, .prod-desc, [class*='desc'], p"
        )
        description = _clean(desc_el.get_text() if desc_el else "")

        link_el = card.select_one("a[href]")
        product_url = link_el["href"] if link_el and link_el.get("href") else ""
        if product_url and not product_url.startswith("http"):
            product_url = "https://www.indiamart.com" + product_url

        price_info = _extract_price(card)
        location = _extract_location(card)

        results.append(
            {
                "product_name": product_name,
                "supplier_name": supplier_name,
                "description": description,
                "product_url": product_url,
                "location": location,
                "category": category,
                **price_info,
            }
        )

    logger.info("Parsed %d products from page (category=%s)", len(results), category)
    return results
