from filters import is_target_country, score_offer, filter_offers


def test_accepts_singapore():
    assert is_target_country("Singapour") is True


def test_accepts_spain():
    assert is_target_country("Espagne") is True


def test_accepts_china():
    assert is_target_country("Chine") is True


def test_accepts_brazil():
    assert is_target_country("Brésil") is True


def test_accepts_japan():
    assert is_target_country("Japon") is True


def test_rejects_france():
    assert is_target_country("France") is False


def test_rejects_germany():
    assert is_target_country("Allemagne") is False


def test_rejects_empty_string():
    assert is_target_country("") is False


def test_case_insensitive():
    assert is_target_country("SINGAPOUR") is True
    assert is_target_country("espagne") is True


def test_score_offer_matches_python():
    offer = {"title": "Développeur Python", "description": "Mission machine learning"}
    result = score_offer(offer)
    assert result["score"] == 2
    assert "python" in result["matched_keywords"]
    assert "machine learning" in result["matched_keywords"]


def test_score_offer_no_match_returns_zero():
    offer = {"title": "Responsable Marketing", "description": "Gestion de campagnes publicitaires"}
    result = score_offer(offer)
    assert result["score"] == 0
    assert result["matched_keywords"] == []


def test_score_offer_case_insensitive():
    offer = {"title": "MACHINE LEARNING Engineer", "description": "AWS Cloud"}
    result = score_offer(offer)
    assert "machine learning" in result["matched_keywords"]
    assert "aws" in result["matched_keywords"]


def test_score_offer_preserves_original_fields():
    offer = {"title": "Data Scientist", "description": "Python NLP", "country": "Japon", "url": "https://example.com"}
    result = score_offer(offer)
    assert result["country"] == "Japon"
    assert result["url"] == "https://example.com"
    assert result["title"] == "Data Scientist"


def test_score_offer_word_boundary_no_false_positives():
    # "rest" should not match "restaurant", "rag" should not match "garage"
    offer = {"title": "Restaurant Manager", "description": "Gestion du garage et du storage"}
    result = score_offer(offer)
    assert "rest" not in result["matched_keywords"]
    assert "rag" not in result["matched_keywords"]


def test_filter_offers_removes_non_target_countries():
    offers = [
        {"title": "Data Scientist Python", "description": "ML project", "country": "Singapour"},
        {"title": "Data Analyst", "description": "SQL analysis", "country": "Allemagne"},
    ]
    result = filter_offers(offers)
    assert len(result) == 1
    assert result[0]["country"] == "Singapour"


def test_filter_offers_removes_zero_score():
    offers = [
        {"title": "Data Scientist Python", "description": "ML cloud AWS", "country": "Japon"},
        {"title": "Responsable RH", "description": "Recrutement et formation", "country": "Espagne"},
    ]
    result = filter_offers(offers)
    assert len(result) == 1
    assert result[0]["title"] == "Data Scientist Python"


def test_filter_offers_sorted_by_score_desc():
    offers = [
        {"title": "Python Developer", "description": "python api rest", "country": "Japon"},
        {"title": "ML Engineer", "description": "machine learning deep learning python nlp aws cloud data science", "country": "Singapour"},
    ]
    result = filter_offers(offers)
    assert result[0]["score"] >= result[1]["score"]


def test_filter_offers_empty_list():
    assert filter_offers([]) == []
