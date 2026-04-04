from dataclasses import dataclass

from config import TARGET_COUNTRIES, PROFILE_KEYWORDS


@dataclass(frozen=True)
class UserProfile:
    name: str
    countries: frozenset[str]
    keywords: tuple[str, ...]
    duration_max: int = 24  # max mission duration in months (inclusive)


PROFILES: dict[str, UserProfile] = {
    "adam": UserProfile(
        name="adam",
        countries=frozenset(TARGET_COUNTRIES),
        keywords=tuple(PROFILE_KEYWORDS),
        duration_max=24,
    ),
    "clotilde": UserProfile(
        name="clotilde",
        countries=frozenset({
            # Western Europe
            "france",
            "espagne", "spain",
            "portugal",
            "italie", "italy",
            "allemagne", "germany",
            "pays-bas", "netherlands",
            "belgique", "belgium",
            "suisse", "switzerland",
            "irlande", "ireland",
            "royaume-uni", "united kingdom",
            "autriche", "austria",
            "luxembourg",
            # Nordic
            "suede", "sweden",
            "danemark", "denmark",
            "finlande", "finland",
            "norvege", "norway",
            # Eastern Europe
            "pologne", "poland",
            "republique tcheque", "czech republic",
            "hongrie", "hungary",
            "roumanie", "romania",
            # Southern Europe
            "grece", "greece",
            "croatie", "croatia",
            "malte", "malta",
            "chypre", "cyprus",
            # Latin America
            "bresil", "brazil",
            "argentine", "argentina",
            "mexique", "mexico",
            "colombie", "colombia",
            "chili", "chile",
            "perou", "peru",
            "uruguay",
            "bolivie", "bolivia",
            "equateur", "ecuador",
            "panama",
            "costa rica",
        }),
        keywords=(
            "commercial",
            "commerciale",
            "vente",
            "sales",
            "business development",
            "developpement commercial",
            "account manager",
            "key account",
            "charge d'affaires",
            "commercial export",
            "commercial international",
            "prospection",
            "negociation",
            "CRM",
            "Salesforce",
            "relation client",
            "B2B",
            "B2C",
            "marketing",
            "communication",
            "chef de zone",
            "export",
            "international trade",
            "developpeur",
            "developer",
            "digital",
        ),
        duration_max=12,
    ),
}
