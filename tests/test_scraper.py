from unittest.mock import MagicMock, patch

from scraper import map_offer, scrape_all_offers


def _raw_offer(**overrides) -> dict:
    base = {
        "id": 123,
        "missionTitle": "Data Scientist",
        "organizationName": "TotalEnergies",
        "countryName": "SINGAPOUR",
        "cityName": "Singapore",
        "missionDescription": "Mission data science et ML",
        "missionProfile": "Python, SQL requis",
        "missionDuration": 12,
        "missionStartDate": "2026-06-01T00:00:00",
        "creationDate": "2026-03-15T10:00:00Z",
    }
    return {**base, **overrides}


def test_map_offer_full():
    result = map_offer(_raw_offer())
    assert result["title"] == "Data Scientist"
    assert result["company"] == "TotalEnergies"
    assert result["country"] == "singapour"
    assert result["city"] == "Singapore"
    assert result["duration"] == "12"
    assert result["start_date"] == "2026-06-01"
    assert result["posted_date"] == "2026-03-15"
    assert result["url"] == "https://mon-vie-via.businessfrance.fr/offres/123"


def test_map_offer_description_combines_fields():
    result = map_offer(_raw_offer(missionDescription="desc part", missionProfile="profile part"))
    assert "desc part" in result["description"]
    assert "profile part" in result["description"]


def test_map_offer_missing_optional_fields_use_empty_string():
    result = map_offer({"id": 1})
    assert result["title"] == ""
    assert result["company"] == ""
    assert result["country"] == ""
    assert result["city"] == ""
    assert result["description"] == ""
    assert result["duration"] == ""
    assert result["start_date"] == ""
    assert result["posted_date"] == ""
    assert result["url"] == "https://mon-vie-via.businessfrance.fr/offres/1"


def test_map_offer_strips_whitespace():
    result = map_offer(_raw_offer(missionTitle="  Analyst  ", organizationName=" Airbus "))
    assert result["title"] == "Analyst"
    assert result["company"] == "Airbus"


def test_map_offer_country_lowercased():
    result = map_offer(_raw_offer(countryName="ETATS-UNIS"))
    assert result["country"] == "etats-unis"


def _make_ctx_mock(responses: list[dict]) -> MagicMock:
    ctx = MagicMock()
    call_count = {"n": 0}

    def post_side_effect(*args, **kwargs):
        resp = MagicMock()
        resp.json.return_value = responses[min(call_count["n"], len(responses) - 1)]
        call_count["n"] += 1
        return resp

    ctx.request.post.side_effect = post_side_effect
    return ctx


def test_scrape_all_offers_paginates():
    first_page = {"count": 3, "result": [_raw_offer(id=1), _raw_offer(id=2)]}
    second_page = {"count": 3, "result": [_raw_offer(id=3)]}

    with patch("scraper.sync_playwright") as mock_pw, \
         patch("scraper.BATCH_SIZE", 2):
        browser = MagicMock()
        ctx = _make_ctx_mock([first_page, second_page])
        browser.new_context.return_value = ctx
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = browser

        result = scrape_all_offers()

    assert len(result) == 3
    assert result[0]["url"].endswith("/1")
    assert result[2]["url"].endswith("/3")


def test_scrape_all_offers_single_page():
    only_page = {"count": 1, "result": [_raw_offer(id=42)]}

    with patch("scraper.sync_playwright") as mock_pw, \
         patch("scraper.BATCH_SIZE", 50):
        browser = MagicMock()
        ctx = _make_ctx_mock([only_page])
        browser.new_context.return_value = ctx
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = browser

        result = scrape_all_offers()

    assert len(result) == 1
    assert result[0]["url"].endswith("/42")


def test_scrape_all_offers_empty():
    empty = {"count": 0, "result": []}

    with patch("scraper.sync_playwright") as mock_pw:
        browser = MagicMock()
        ctx = _make_ctx_mock([empty])
        browser.new_context.return_value = ctx
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = browser

        result = scrape_all_offers()

    assert result == []
