import re
import unicodedata
from datetime import date
from typing import TYPE_CHECKING

from config import TARGET_COUNTRIES, PROFILE_KEYWORDS

if TYPE_CHECKING:
    from profiles import UserProfile

_KEYWORD_PATTERNS: list[tuple[str, re.Pattern]] = [
    (kw, re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)) for kw in PROFILE_KEYWORDS
]

_NORMALIZED_COUNTRIES: set[str] = {
    unicodedata.normalize("NFD", c).encode("ascii", "ignore").decode()
    for c in TARGET_COUNTRIES
}


def _normalize(s: str) -> str:
    return unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()


def _build_patterns(keywords: tuple[str, ...] | list[str]) -> list[tuple[str, re.Pattern]]:
    return [
        (kw, re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE))
        for kw in keywords
    ]


def _score_with_patterns(offer: dict, patterns: list[tuple[str, re.Pattern]]) -> dict:
    searchable = f"{offer.get('title', '')} {offer.get('description', '')}".lower()
    matched = [kw for kw, pat in patterns if pat.search(searchable)]
    return {**offer, "score": len(matched), "matched_keywords": matched}


def _is_active(offer: dict) -> bool:
    expiry = offer.get("expiry_date", "")
    if not expiry:
        return True
    return expiry >= date.today().isoformat()


def _meets_duration(offer: dict, max_duration: int) -> bool:
    try:
        return int(offer.get("duration", 0)) <= max_duration
    except (ValueError, TypeError):
        return True


def is_target_country(country: str) -> bool:
    return _normalize(country) in _NORMALIZED_COUNTRIES


def score_offer(offer: dict) -> dict:
    return _score_with_patterns(offer, _KEYWORD_PATTERNS)


def filter_offers(offers: list[dict], profile: "UserProfile | None" = None) -> list[dict]:
    if profile is None:
        patterns = _KEYWORD_PATTERNS
        normalized_countries = _NORMALIZED_COUNTRIES
        duration_max = None
    else:
        patterns = _build_patterns(profile.keywords)
        normalized_countries = {_normalize(c) for c in profile.countries}
        duration_max = profile.duration_max

    candidates = [
        o for o in offers
        if _normalize(o.get("country", "")) in normalized_countries
        and _is_active(o)
        and (duration_max is None or _meets_duration(o, duration_max))
    ]
    scored = [_score_with_patterns(o, patterns) for o in candidates]
    matching = [o for o in scored if o["score"] > 0]
    return sorted(matching, key=lambda o: o["score"], reverse=True)
