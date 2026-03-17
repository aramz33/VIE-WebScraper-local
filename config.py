from pathlib import Path
from datetime import date

OUTPUT_DIR = Path("output")


def get_output_file() -> Path:
    return OUTPUT_DIR / f"offres_{date.today().isoformat()}.csv"

BASE_URL = "https://mon-vie-via.businessfrance.fr/offres"

MAX_SCROLL_ATTEMPTS = 50
SCROLL_PAUSE_MS = 1500
PAGE_LOAD_TIMEOUT_MS = 30_000

TARGET_COUNTRIES: set[str] = {
    # Asia
    "singapour", "singapore",
    "japon", "japan",
    "corée du sud", "south korea", "korea",
    "chine", "china",
    "inde", "india",
    "thaïlande", "thailand",
    "vietnam", "viêt nam",
    "hong kong",
    "taïwan", "taiwan",
    "malaisie", "malaysia",
    "indonésie", "indonesia",
    "philippines",
    "australie", "australia",
    "nouvelle-zélande", "new zealand",
    # Mediterranean Europe
    "espagne", "spain",
    "italie", "italy",
    "portugal",
    "grèce", "greece",
    "maroc", "morocco",
    "tunisie", "tunisia",
    "algérie", "algeria",
    "égypte", "egypt",
    "turquie", "turkey",
    "croatie", "croatia",
    "malte", "malta",
    "chypre", "cyprus",
    # North America
    "états-unis", "united states", "usa",
    "canada",
    # South America
    "brésil", "brazil",
    "argentine", "argentina",
    "mexique", "mexico",
    "colombie", "colombia",
    "chili", "chile",
    "pérou", "peru",
    "uruguay",
}

PROFILE_KEYWORDS: list[str] = [
    "machine learning",
    "data science",
    "artificial intelligence",
    "intelligence artificielle",
    "python",
    "llm",
    "nlp",
    "natural language processing",
    "deep learning",
    "mlops",
    "data engineer",
    "data analyst",
    "data scientist",
    "cloud",
    "aws",
    "backend",
    "fastapi",
    "django",
    "rag",
    "agentic",
    "computer vision",
    "pytorch",
    "tensorflow",
    "huggingface",
    "big data",
    "sql",
    "data pipeline",
    "api",
    "rest",
    "microservices",
    "automation",
    "forecasting",
    "supply chain",
    "recommendation system",
    "données",
    "apprentissage automatique",
    "modèle",
]
