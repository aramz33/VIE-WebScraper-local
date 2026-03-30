import re
import unicodedata
from datetime import date

from config import TARGET_COUNTRIES, PROFILE_KEYWORDS

# Pre-compile patterns once at module load — avoids recompiling per offer
_KEYWORD_PATTERNS: list[tuple[str, re.Pattern]] = [
    (kw, re.compile(rf"\b{re.escape(kw)}\b")) for kw in PROFILE_KEYWORDS
]

_NORMALIZED_COUNTRIES: set[str] = {
    unicodedata.normalize("NFD", c).encode("ascii", "ignore").decode()
    for c in TARGET_COUNTRIES
}


def _normalize(s: str) -> str:
    return unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()


def is_target_country(country: str) -> bool:
    return _normalize(country) in _NORMALIZED_COUNTRIES


def score_offer(offer: dict) -> dict:
    searchable = f"{offer.get('title', '')} {offer.get('description', '')}".lower()
    matched = [kw for kw, pattern in _KEYWORD_PATTERNS if pattern.search(searchable)]
    return {
        **offer,
        "score": len(matched),
        "matched_keywords": matched,
    }


def _is_active(offer: dict) -> bool:
    expiry = offer.get("expiry_date", "")
    if not expiry:
        return True
    return expiry >= date.today().isoformat()


def filter_offers(offers: list[dict]) -> list[dict]:
    candidates = [o for o in offers if is_target_country(o.get("country", "")) and _is_active(o)]
    scored = [score_offer(o) for o in candidates]
    matching = [o for o in scored if o["score"] > 0]
    return sorted(matching, key=lambda o: o["score"], reverse=True)
