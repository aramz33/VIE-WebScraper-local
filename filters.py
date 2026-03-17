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


def filter_offers(offers: list[dict]) -> list[dict]:
    scored = [score_offer(o) for o in offers if is_target_country(o.get("country", ""))]
    matching = [o for o in scored if o["score"] > 0]
    return sorted(matching, key=lambda o: o["score"], reverse=True)
