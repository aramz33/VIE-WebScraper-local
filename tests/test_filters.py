import pytest
from filters import is_target_country


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
