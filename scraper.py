from __future__ import annotations
import json

from playwright.sync_api import sync_playwright

from config import BASE_DOMAIN, SEARCH_API_URL, BATCH_SIZE

_SEARCH_HEADERS = {
    "Content-Type": "application/json",
    "Origin": BASE_DOMAIN,
}

_SEARCH_PAYLOAD_BASE: dict = {
    "sort": ["0"],
    "activitySectorId": [],
    "missionsTypesIds": [],
    "missionsDurations": [],
    "geographicZones": [],
    "countriesIds": [],
    "studiesLevelId": [],
    "companiesSizes": [],
    "specializationsIds": [],
    "entreprisesIds": [0],
    "missionStartDate": None,
    "query": None,
}


def map_offer(raw: dict) -> dict:
    description = (raw.get("missionDescription") or "") + " " + (raw.get("missionProfile") or "")
    return {
        "title": (raw.get("missionTitle") or "").strip(),
        "company": (raw.get("organizationName") or "").strip(),
        "country": (raw.get("countryName") or "").lower().strip(),
        "city": (raw.get("cityName") or "").strip(),
        "description": description.strip(),
        "duration": str(raw.get("missionDuration") or ""),
        "start_date": (raw.get("missionStartDate") or "")[:10],
        "posted_date": (raw.get("creationDate") or "")[:10],
        "expiry_date": (raw.get("endBroadcastDate") or "")[:10],
        "url": f"{BASE_DOMAIN}/offres/{raw['id']}",
    }


def _search(ctx, skip: int, limit: int) -> dict:
    payload = json.dumps({**_SEARCH_PAYLOAD_BASE, "limit": limit, "skip": skip})
    resp = ctx.request.post(SEARCH_API_URL, data=payload, headers=_SEARCH_HEADERS)
    return resp.json()


def scrape_all_offers() -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            ctx = browser.new_context()
            first = _search(ctx, skip=0, limit=BATCH_SIZE)
            total = first.get("count", 0)
            all_raw = list(first.get("result", []))

            for skip in range(BATCH_SIZE, total, BATCH_SIZE):
                batch = _search(ctx, skip=skip, limit=BATCH_SIZE)
                all_raw.extend(batch.get("result", []))

            return [map_offer(o) for o in all_raw]
        finally:
            browser.close()
