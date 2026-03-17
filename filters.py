import re

from config import TARGET_COUNTRIES, PROFILE_KEYWORDS

# Pre-compile patterns once at module load — avoids recompiling per offer
_KEYWORD_PATTERNS: list[tuple[str, re.Pattern]] = [
    (kw, re.compile(rf"\b{re.escape(kw)}\b")) for kw in PROFILE_KEYWORDS
]


def is_target_country(country: str) -> bool:
    return country.strip().lower() in TARGET_COUNTRIES


def score_offer(offer: dict) -> dict:
    searchable = f"{offer.get('title', '')} {offer.get('description', '')}".lower()
    matched = [kw for kw, pattern in _KEYWORD_PATTERNS if pattern.search(searchable)]
    return {
        **offer,
        "score": len(matched),
        "matched_keywords": matched,
    }
