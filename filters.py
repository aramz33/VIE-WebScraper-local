import re

from config import TARGET_COUNTRIES, PROFILE_KEYWORDS


def is_target_country(country: str) -> bool:
    return country.strip().lower() in TARGET_COUNTRIES


def score_offer(offer: dict) -> dict:
    searchable = f"{offer.get('title', '')} {offer.get('description', '')}".lower()
    # Use word boundary matching to avoid false positives (e.g. "rest" in "restaurant")
    # dict.fromkeys preserves insertion order and deduplicates
    matched = list(dict.fromkeys(
        kw for kw in PROFILE_KEYWORDS
        if re.search(rf"\b{re.escape(kw)}\b", searchable)
    ))
    return {
        **offer,
        "score": len(matched),
        "matched_keywords": matched,
    }
