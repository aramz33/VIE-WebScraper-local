@~/.claude/lang-rules/python/coding-style.md
@~/.claude/lang-rules/python/testing.md
@~/.claude/lang-rules/python/patterns.md
@~/.claude/lang-rules/python/security.md
@~/.claude/lang-rules/python/hooks.md

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Run scraper
python run.py

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing --ignore=.venv

# Run a single test file
pytest tests/test_filters.py

# Run a single test by name
pytest tests/test_filters.py::test_score_offer_matches_python -v
```

## Architecture

The pipeline is linear: **scrape → filter → export**.

```
run.py          — orchestrator: calls scrape_all_offers() → filter_offers() → CSV export
scraper.py      — Playwright browser automation: infinite scroll + DOM extraction
filters.py      — pure functions: country allow-list + keyword scoring + ranking
config.py       — all constants: URL, selectors, TARGET_COUNTRIES, PROFILE_KEYWORDS
tests/          — pytest unit tests (mock-based for scraper, pure-function for filters)
output/         — generated CSV files (gitignored), named offres_YYYY-MM-DD.csv
```

### Key Design Points

**`config.py` is the single source of truth.** All tunable parameters live here — target countries, profile keywords, scroll behaviour, CSS selectors. To add/remove countries or keywords, only edit `config.py`.

**`filters.py` is pure.** No I/O, no side effects. `filter_offers(offers)` does: country check → keyword scoring → zero-score drop → sort by score descending. `score_offer` returns a new dict with `score` and `matched_keywords` added (never mutates input).

**`scraper.py` uses Playwright sync API.** `scrape_all_offers()` launches headless Chromium, scrolls until stable (3 consecutive unchanged card counts), then extracts all offer cards. The browser is always closed in a `finally` block.

**`run.py` uses pandas for CSV export.** The `matched_keywords` list is joined to a comma-separated string before writing. Output columns are ordered by `CSV_COLUMNS` (score first, description last).

**CSS selectors are known-fragile.** `SELECTORS["duration"]`, `"start_date"`, and `"posted_date"` all point to `.meta-list` — a TODO stub. These fields will contain the full meta list text until the selectors are refined via live DOM inspection.

**Tests mock Playwright objects.** `test_scraper.py` uses `unittest.mock.MagicMock` to simulate `page` and `card` objects. The mock's `query_selector` side effect maps CSS selectors (from `SELECTORS`) to fake elements. Scraper tests never launch a real browser.

### Data Flow Detail

```
scraper.py: card DOM → extract_offers_from_page() → list[dict] with OFFER_FIELDS
                        ↓ _parse_location() splits "COUNTRY - CITY" → country (lowercase), city
filters.py: list[dict] → is_target_country() check → score_offer() → filter zero-score → sort
run.py:     filtered list[dict] → pd.DataFrame(columns=CSV_COLUMNS) → CSV
```

The `country` field is always lowercase after scraping (used for set membership check against `TARGET_COUNTRIES`). The original casing from the DOM is lost.
