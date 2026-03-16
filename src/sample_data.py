"""
Generates realistic sample data that mirrors the structure of actual
IndiaMART scrape results. Used as a fallback when live scraping is
blocked or for offline development/testing of the ETL + EDA pipeline.
"""

import json
import os
import random
from datetime import datetime, timezone

from src.config import RAW_DATA_DIR

random.seed(42)

_CATEGORIES = {
    "industrial-machinery": {
        "products": [
            "CNC Lathe Machine", "Hydraulic Press", "Industrial Compressor",
            "Milling Machine", "Conveyor Belt System", "Welding Machine",
            "Drilling Machine", "Grinding Machine", "Packaging Machine",
            "Injection Moulding Machine", "Laser Cutting Machine", "Forklift",
            "Boiler System", "Generator Set", "Crane Hoist",
            "Centrifugal Pump", "Industrial Oven", "Sheet Metal Press",
            "Lathe Chuck", "Ball Bearing Unit", "Gear Box Assembly",
            "Air Compressor 5HP", "Diesel Generator 10KVA", "Vibrating Screen",
            "Jaw Crusher", "Concrete Mixer", "Tower Crane",
        ],
        "price_range": (15000, 2500000),
        "units": ["Piece", "Unit", "Set", "Number"],
    },
    "electronics-components": {
        "products": [
            "Arduino Uno Board", "Raspberry Pi 4", "MOSFET Transistor",
            "LED Strip Light 5m", "Capacitor 100uF", "Resistor Kit 1000pcs",
            "PCB Prototype Board", "Soldering Station", "Oscilloscope 100MHz",
            "Relay Module 8-Channel", "Servo Motor SG90", "Stepper Motor NEMA17",
            "Power Supply 12V 10A", "Voltage Regulator LM7805", "IC Socket DIP-8",
            "Copper Wire 1mm", "Heat Sink Aluminium", "Thermal Paste",
            "Multimeter Digital", "Logic Analyzer", "Signal Generator",
            "Breadboard 830 Points", "Jumper Wire Kit", "Battery 18650 Li-ion",
            "Solar Panel 100W", "Inverter 1KVA", "UPS System 3KVA",
        ],
        "price_range": (50, 75000),
        "units": ["Piece", "Kit", "Pack", "Meter", "Set"],
    },
    "textiles-fabrics": {
        "products": [
            "Cotton Fabric Roll", "Silk Saree Material", "Polyester Blend Fabric",
            "Denim Fabric 12oz", "Linen Fabric Premium", "Chiffon Fabric",
            "Velvet Upholstery Fabric", "Rayon Printed Fabric", "Wool Tweed Fabric",
            "Jute Bag Material", "Nylon Ripstop Fabric", "Lycra Stretch Fabric",
            "Organza Fabric", "Georgette Fabric", "Muslin Cotton Fabric",
            "Terry Towel Fabric", "Canvas Heavy Duty", "Satin Fabric",
            "Embroidered Fabric", "Block Print Cotton", "Khadi Handloom Fabric",
            "Bamboo Fiber Fabric", "Tussar Silk Fabric", "Chanderi Fabric",
            "Banarasi Brocade", "Ikat Fabric", "Kalamkari Fabric",
        ],
        "price_range": (80, 5000),
        "units": ["Meter", "Yard", "Kg", "Roll"],
    },
}

_CITIES = [
    ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bangalore", "Karnataka"),
    ("Chennai", "Tamil Nadu"), ("Hyderabad", "Telangana"), ("Ahmedabad", "Gujarat"),
    ("Pune", "Maharashtra"), ("Kolkata", "West Bengal"), ("Jaipur", "Rajasthan"),
    ("Surat", "Gujarat"), ("Lucknow", "Uttar Pradesh"), ("Kanpur", "Uttar Pradesh"),
    ("Nagpur", "Maharashtra"), ("Indore", "Madhya Pradesh"), ("Coimbatore", "Tamil Nadu"),
    ("Ludhiana", "Punjab"), ("Rajkot", "Gujarat"), ("Vadodara", "Gujarat"),
    ("Faridabad", "Haryana"), ("Gurgaon", "Haryana"), ("Noida", "Uttar Pradesh"),
    ("Thane", "Maharashtra"), ("Ernakulam", "Kerala"), ("Bhopal", "Madhya Pradesh"),
    ("Visakhapatnam", "Andhra Pradesh"), ("Tirupur", "Tamil Nadu"),
    ("Panipat", "Haryana"), ("Moradabad", "Uttar Pradesh"),
]

_SUPPLIER_PREFIXES = [
    "Shree", "Sri", "Royal", "National", "Global", "Star", "Prime",
    "Excel", "Supreme", "Apex", "Reliable", "Modern", "Pioneer",
    "Universal", "Standard", "Classic", "Elite", "Precision",
]

_SUPPLIER_SUFFIXES = [
    "Industries", "Enterprises", "Trading Co.", "Engineers",
    "Manufacturing", "Solutions", "Corporation", "Pvt. Ltd.",
    "Exports", "Traders", "Works", "Tech", "Systems",
]


def _random_supplier() -> str:
    return f"{random.choice(_SUPPLIER_PREFIXES)} {random.choice(_SUPPLIER_SUFFIXES)}"


def _random_price(lo: int, hi: int) -> dict:
    has_price = random.random() > 0.15  # ~85% have prices
    if not has_price:
        return {"price_raw": "", "price_min": None, "price_max": None, "price_unit": None}

    p1 = random.randint(lo, hi)
    has_range = random.random() > 0.6
    p2 = random.randint(p1, int(p1 * 1.5)) if has_range else None
    unit = None  # will be filled by caller

    raw_parts = [f"Rs. {p1:,}"]
    if p2:
        raw_parts.append(f"Rs. {p2:,}")

    return {
        "price_raw": " - ".join(raw_parts),
        "price_min": str(p1),
        "price_max": str(p2) if p2 else None,
        "price_unit": unit,
    }


def generate_sample_data(records_per_category: int = 150) -> str:
    """
    Generate sample data and write it to data/raw/ as JSON.
    Returns the output file path.
    """
    all_records = []

    for cat_key, cat_info in _CATEGORIES.items():
        for _ in range(records_per_category):
            product = random.choice(cat_info["products"])
            variant = random.choice(["", " - Standard", " - Premium", " - Heavy Duty", " - Compact", ""])
            city, state = random.choice(_CITIES)
            price = _random_price(*cat_info["price_range"])
            price["price_unit"] = random.choice(cat_info["units"])

            if price["price_raw"] and price["price_unit"]:
                price["price_raw"] += f" / {price['price_unit']}"

            record = {
                "product_name": product + variant,
                "supplier_name": _random_supplier(),
                "description": f"High quality {product.lower()} available for bulk and retail orders. "
                               f"Manufactured using premium materials with industry certifications.",
                "product_url": f"https://www.indiamart.com/proddetail/{cat_key}-{random.randint(10000, 99999)}.html",
                "location": f"{city}, {state}",
                "category": cat_key,
                **price,
            }
            all_records.append(record)

    random.shuffle(all_records)

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(RAW_DATA_DIR, f"indiamart_raw_{ts}.json")

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "scraped_at": ts,
                "total_records": len(all_records),
                "categories": list(_CATEGORIES.keys()),
                "data": all_records,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )

    print(f"[OK] Generated {len(all_records)} sample records -> {out_path}")
    return out_path
