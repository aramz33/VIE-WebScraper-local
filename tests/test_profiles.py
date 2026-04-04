import pytest

from filters import filter_offers, _meets_duration
from profiles import UserProfile, PROFILES

CLOTILDE = PROFILES["clotilde"]
ADAM = PROFILES["adam"]

_BASE_OFFER = {
    "title": "",
    "description": "",
    "country": "espagne",
    "duration": "6",
    "expiry_date": "9999-12-31",
}


def _offer(**kwargs) -> dict:
    return {**_BASE_OFFER, **kwargs}


# ---------------------------------------------------------------------------
# _meets_duration
# ---------------------------------------------------------------------------

def test_meets_duration_within_limit():
    assert _meets_duration(_offer(duration="6"), 12) is True


def test_meets_duration_at_limit():
    assert _meets_duration(_offer(duration="12"), 12) is True


def test_meets_duration_exceeds_limit():
    assert _meets_duration(_offer(duration="18"), 12) is False


def test_meets_duration_unparseable_passes():
    assert _meets_duration(_offer(duration="N/A"), 12) is True


def test_meets_duration_missing_passes():
    assert _meets_duration({}, 12) is True


# ---------------------------------------------------------------------------
# filter_offers with clotilde profile
# ---------------------------------------------------------------------------

def test_clotilde_filters_by_duration():
    long_offer = _offer(title="Commercial B2B", duration="18")
    short_offer = _offer(title="Commercial B2B", duration="6")
    result = filter_offers([long_offer, short_offer], profile=CLOTILDE)
    assert len(result) == 1
    assert result[0]["duration"] == "6"


def test_clotilde_filters_by_country():
    eu_offer = _offer(title="Commercial export", country="espagne", duration="6")
    asia_offer = _offer(title="Commercial export", country="singapour", duration="6")
    result = filter_offers([eu_offer, asia_offer], profile=CLOTILDE)
    assert len(result) == 1
    assert result[0]["country"] == "espagne"


def test_clotilde_keyword_match():
    offer = _offer(title="Chargé de développement commercial B2B", country="portugal", duration="6")
    result = filter_offers([offer], profile=CLOTILDE)
    assert len(result) == 1
    assert result[0]["score"] > 0


def test_clotilde_zero_score_excluded():
    offer = _offer(title="Offre sans mot-clé pertinent", country="espagne", duration="6")
    result = filter_offers([offer], profile=CLOTILDE)
    assert result == []


def test_clotilde_sorted_by_score_desc():
    low = _offer(title="commercial", country="france", duration="6")
    high = _offer(title="commercial vente sales B2B B2C marketing", country="france", duration="6")
    result = filter_offers([low, high], profile=CLOTILDE)
    assert result[0]["score"] >= result[1]["score"]


# ---------------------------------------------------------------------------
# Backward compatibility: no profile uses default config
# ---------------------------------------------------------------------------

def test_no_profile_uses_default_config():
    offer = _offer(title="machine learning python", country="singapour", duration="24")
    result = filter_offers([offer], profile=None)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# PROFILES registry
# ---------------------------------------------------------------------------

def test_profiles_registry_has_adam():
    assert "adam" in PROFILES


def test_profiles_registry_has_clotilde():
    assert "clotilde" in PROFILES


def test_clotilde_duration_max_is_12():
    assert CLOTILDE.duration_max == 12


def test_adam_duration_max_is_24():
    assert ADAM.duration_max == 24
