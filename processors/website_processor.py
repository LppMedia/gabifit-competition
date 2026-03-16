"""
Extract pricing and service information from scraped website Markdown.

Input:
  data/raw/websites_raw.json

Output:
  data/processed/services_pricing.csv
"""

import json
import os
import re
import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# RD$ to USD exchange rate (approximate)
RD_TO_USD = 1 / 57.0

# Price patterns (match RD$ and USD amounts)
PRICE_PATTERNS = [
    r"RD\$\s*([\d,]+)",
    r"RD\s*([\d,]+)",
    r"\$\s*([\d,]+)\s*(?:USD|usd|dólares|dolares)?",
    r"([\d,]+)\s*(?:pesos|RD\$)",
]

SERVICE_KEYWORDS = {
    "offers_online": [
        "online", "virtual", "remoto", "a distancia", "whatsapp coaching",
        "plan online", "coaching online",
    ],
    "offers_in_person": [
        "presencial", "personal training", "entrenamiento personal",
        "en persona", "gym", "sede",
    ],
    "offers_nutrition": [
        "plan nutricional", "nutricion", "nutrición", "dieta", "meal plan",
        "plan de comida", "alimentacion", "alimentación",
    ],
    "offers_transformation": [
        "transformacion", "transformación", "reto", "challenge",
        "programa de", "plan de transformacion",
    ],
    "offers_group": [
        "clases grupales", "bootcamp", "grupo", "clase grupal",
    ],
}

LEAD_MAGNET_KEYWORDS = {
    "ebook": ["ebook", "e-book", "libro digital", "libro gratis"],
    "free_workout": ["rutina gratis", "free workout", "workout gratis", "entrenamiento gratis"],
    "challenge": ["reto gratuito", "reto gratis", "challenge gratis", "free challenge"],
    "calculator": ["calculadora", "calculator", "calcula tu"],
    "guide": ["guia gratuita", "guía gratuita", "guia gratis", "guía gratis", "descarga gratis"],
}


def _extract_prices(text: str) -> tuple:
    """Return (min_price_usd, max_price_usd, currency_detected)."""
    if not text:
        return None, None, "none"

    text_lower = text.lower()
    raw_prices = []
    is_rd = False

    for pat in PRICE_PATTERNS:
        for match in re.finditer(pat, text, re.IGNORECASE):
            try:
                val = float(match.group(1).replace(",", ""))
                raw_prices.append(val)
            except (ValueError, IndexError):
                continue

    if not raw_prices:
        return None, None, "none"

    # Detect currency
    if re.search(r"RD\$|pesos|RD\s+\d", text, re.IGNORECASE):
        is_rd = True
        currency = "RD"
    elif re.search(r"\$|USD|dólar|dollar", text, re.IGNORECASE):
        currency = "USD"
    else:
        currency = "mixed"
        is_rd = True  # Assume RD$ if ambiguous in DR context

    # Filter out unrealistic values (< 100 is probably not a price)
    raw_prices = [p for p in raw_prices if p >= 100]
    if not raw_prices:
        return None, None, "none"

    if is_rd:
        prices_usd = [round(p * RD_TO_USD, 2) for p in raw_prices]
    else:
        prices_usd = raw_prices

    # Cap sanity check
    prices_usd = [p for p in prices_usd if p <= 2000]
    if not prices_usd:
        return None, None, currency

    return round(min(prices_usd), 2), round(max(prices_usd), 2), currency


def _detect_services(text: str) -> dict:
    if not text:
        return {k: False for k in SERVICE_KEYWORDS}
    text_lower = text.lower()
    return {
        key: any(kw in text_lower for kw in keywords)
        for key, keywords in SERVICE_KEYWORDS.items()
    }


def _detect_lead_magnet(text: str) -> tuple:
    if not text:
        return False, "none"
    text_lower = text.lower()
    for magnet_type, keywords in LEAD_MAGNET_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return True, magnet_type
    return False, "none"


def process_entry(entry: dict) -> dict:
    username = entry.get("coach_username", "unknown")
    content = entry.get("markdown_content", "")
    url = entry.get("url", "")
    has_website = not url.startswith("search:")

    min_price, max_price, currency = _extract_prices(content)
    services = _detect_services(content)
    has_lead_magnet, lead_magnet_type = _detect_lead_magnet(content)

    text_lower = content.lower()
    has_whatsapp_cta = any(kw in text_lower for kw in ["whatsapp", "wa.me", "escríbeme", "escribeme"])
    has_contact_form = any(kw in text_lower for kw in ["contacto", "formulario", "contact", "form"])
    uses_linktree = "linktree" in text_lower or "linktr.ee" in text_lower
    has_pricing_page = min_price is not None

    return {
        "coach_username": username,
        "has_website": has_website,
        "has_pricing_page": has_pricing_page,
        "min_price_usd": min_price,
        "max_price_usd": max_price,
        "currency_detected": currency,
        **services,
        "has_lead_magnet": has_lead_magnet,
        "lead_magnet_type": lead_magnet_type,
        "has_whatsapp_cta": has_whatsapp_cta,
        "has_contact_form": has_contact_form,
        "uses_linktree": uses_linktree,
    }


def run() -> pd.DataFrame:
    path = os.path.join(RAW_DIR, "websites_raw.json")
    if not os.path.exists(path):
        print("[website_processor] No websites_raw.json found.")
        return pd.DataFrame()

    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = [process_entry(entry) for entry in raw]
    df = pd.DataFrame(rows)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DIR, "services_pricing.csv")
    df.to_csv(out_path, index=False)
    print(f"[website_processor] Saved {len(df)} entries -> {out_path}")

    return df


if __name__ == "__main__":
    df = run()
    print(df[["coach_username", "min_price_usd", "max_price_usd", "has_lead_magnet"]].to_string())
