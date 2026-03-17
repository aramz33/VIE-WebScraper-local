from __future__ import annotations

OFFER_FIELDS = ["title", "company", "country", "city", "description", "duration", "start_date", "posted_date", "url"]


def parse_offer_card(raw: dict) -> dict:
    return {field: str(raw.get(field, "")).strip() for field in OFFER_FIELDS}
