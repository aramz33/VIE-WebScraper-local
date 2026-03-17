from config import TARGET_COUNTRIES, PROFILE_KEYWORDS


def is_target_country(country: str) -> bool:
    return country.strip().lower() in TARGET_COUNTRIES
