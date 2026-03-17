import pytest
from filters import is_target_country, score_offer


def test_accepts_singapore():
    assert is_target_country("Singapour") is True


def test_accepts_spain():
    assert is_target_country("Espagne") is True


def test_accepts_usa():
    assert is_target_country("États-Unis") is True


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
    offer = {"title": "Développeur Python Data", "description": "Mission Python et machine learning"}
    result = score_offer(offer)
    assert result["score"] >= 2
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


def test_score_offer_deduplicates_keywords():
    # "data science" and "data scientist" both appear; if they match, score should count each once
    offer = {"title": "Data Scientist", "description": "data science python"}
    result = score_offer(offer)
    # Score should not be inflated by duplicates
    assert result["score"] == len(result["matched_keywords"])
