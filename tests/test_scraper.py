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
