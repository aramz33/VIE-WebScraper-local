from __future__ import annotations

from playwright.sync_api import sync_playwright, Page

from config import BASE_URL, MAX_SCROLL_ATTEMPTS, SCROLL_PAUSE_MS, PAGE_LOAD_TIMEOUT_MS, SELECTORS

OFFER_FIELDS = ["title", "company", "country", "city", "description", "duration", "start_date", "posted_date", "url"]


def parse_offer_card(raw: dict) -> dict:
    return {field: str(raw.get(field, "")).strip() for field in OFFER_FIELDS}


def _get_element_text(card, selector: str) -> str:
    el = card.query_selector(selector)
    return el.inner_text().strip() if el else ""


def extract_offers_from_page(page: Page) -> list[dict]:
    cards = page.query_selector_all(SELECTORS["card"])
    raw_offers = []
    for card in cards:
        link_el = card.query_selector(SELECTORS["link"])
        url = link_el.get_attribute("href") if link_el else ""
        if url and not url.startswith("http"):
            url = f"https://mon-vie-via.businessfrance.fr{url}"
        raw_offers.append(parse_offer_card({
            "title": _get_element_text(card, SELECTORS["title"]),
            "company": _get_element_text(card, SELECTORS["company"]),
            "country": _get_element_text(card, SELECTORS["country"]),
            "city": _get_element_text(card, SELECTORS["city"]),
            "description": _get_element_text(card, SELECTORS.get("description", "")),
            "duration": _get_element_text(card, SELECTORS["duration"]),
            "start_date": _get_element_text(card, SELECTORS["start_date"]),
            "posted_date": _get_element_text(card, SELECTORS["posted_date"]),
            "url": url,
        }))
    return raw_offers


def scroll_until_loaded(page: Page) -> None:
    previous_count = 0
    for _ in range(MAX_SCROLL_ATTEMPTS):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(SCROLL_PAUSE_MS)
        current_count = len(page.query_selector_all(SELECTORS["card"]))
        if current_count == previous_count:
            break
        previous_count = current_count


def scrape_all_offers() -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL, timeout=PAGE_LOAD_TIMEOUT_MS)
        page.wait_for_selector(SELECTORS["card"], timeout=PAGE_LOAD_TIMEOUT_MS)
        scroll_until_loaded(page)
        offers = extract_offers_from_page(page)
        browser.close()
    return offers
