from scraper import parse_offer_card


def test_parse_offer_card_full():
    mock_card = {
        "title": "Data Scientist",
        "company": "TotalEnergies",
        "country": "Singapour",
        "city": "Singapore",
        "description": "Mission data science et ML",
        "duration": "12 mois",
        "start_date": "01/06/2026",
        "posted_date": "15/03/2026",
        "url": "https://mon-vie-via.businessfrance.fr/offres/12345",
    }
    result = parse_offer_card(mock_card)
    assert result["title"] == "Data Scientist"
    assert result["company"] == "TotalEnergies"
    assert result["country"] == "Singapour"
    assert result["url"] == "https://mon-vie-via.businessfrance.fr/offres/12345"


def test_parse_offer_card_missing_fields_uses_empty_string():
    mock_card = {"title": "ML Engineer"}
    result = parse_offer_card(mock_card)
    assert result["company"] == ""
    assert result["country"] == ""
    assert result["description"] == ""
    assert result["url"] == ""


def test_parse_offer_card_strips_whitespace():
    mock_card = {"title": "  Data Analyst  ", "company": " Airbus ", "country": "Espagne "}
    result = parse_offer_card(mock_card)
    assert result["title"] == "Data Analyst"
    assert result["company"] == "Airbus"
    assert result["country"] == "Espagne"


from unittest.mock import MagicMock
from scraper import extract_offers_from_page


def _make_mock_card(title="Data Scientist", company="Airbus", country="Singapour",
                    city="Singapore", duration="12 mois", start_date="01/06/2026",
                    posted_date="15/03/2026", href="/offres/123"):
    def make_text_el(text):
        el = MagicMock()
        el.inner_text.return_value = text
        return el

    link_el = MagicMock()
    link_el.get_attribute.return_value = href

    card = MagicMock()

    def query_selector_side_effect(sel):
        mapping = {
            ".offre-card__title": make_text_el(title),
            ".offre-card__company": make_text_el(company),
            ".offre-card__country": make_text_el(country),
            ".offre-card__city": make_text_el(city),
            ".offre-card__duration": make_text_el(duration),
            ".offre-card__start-date": make_text_el(start_date),
            ".offre-card__posted-date": make_text_el(posted_date),
            "a": link_el,
        }
        return mapping.get(sel, None)

    card.query_selector.side_effect = query_selector_side_effect
    return card


def test_extract_offers_returns_list_of_dicts():
    page = MagicMock()
    page.query_selector_all.return_value = [_make_mock_card()]
    result = extract_offers_from_page(page)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["title"] == "Data Scientist"
    assert result[0]["company"] == "Airbus"
    assert result[0]["country"] == "Singapour"


def test_extract_offers_converts_relative_url():
    page = MagicMock()
    page.query_selector_all.return_value = [_make_mock_card(href="/offres/42")]
    result = extract_offers_from_page(page)
    assert result[0]["url"] == "https://mon-vie-via.businessfrance.fr/offres/42"


def test_extract_offers_keeps_absolute_url():
    page = MagicMock()
    page.query_selector_all.return_value = [_make_mock_card(href="https://example.com/offres/99")]
    result = extract_offers_from_page(page)
    assert result[0]["url"] == "https://example.com/offres/99"


def test_extract_offers_empty_page():
    page = MagicMock()
    page.query_selector_all.return_value = []
    result = extract_offers_from_page(page)
    assert result == []
