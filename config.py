from pathlib import Path
from datetime import date

OUTPUT_DIR = Path("output")


def get_output_file() -> Path:
    return OUTPUT_DIR / f"offres_{date.today().isoformat()}.csv"

BASE_DOMAIN = "https://mon-vie-via.businessfrance.fr"
SEARCH_API_URL = "https://civiweb-api-prd.azurewebsites.net/api/Offers/search"

BATCH_SIZE = 50

TARGET_COUNTRIES: set[str] = {
    # Asia
    "singapour", "singapore",
    "japon", "japan",
    "coree du sud", "south korea", "korea",
    "chine", "china",
    "inde", "india",
    "thailande", "thailand",
    "vietnam", "viet nam",
    "hong kong",
    "taiwan",
    "malaisie", "malaysia",
    "indonesie", "indonesia",
    "philippines",
    "australie", "australia",
    "nouvelle-zelande", "new zealand",
    # Mediterranean Europe
    "espagne", "spain",
    "italie", "italy",
    "portugal",
    "grece", "greece",
    "maroc", "morocco",
    "tunisie", "tunisia",
    "algerie", "algeria",
    "egypte", "egypt",
    "turquie", "turkey",
    "croatie", "croatia",
    "malte", "malta",
    "chypre", "cyprus",
    # North America
    "etats-unis", "united states", "usa",
    "canada",
    # South America
    "bresil", "brazil",
    "argentine", "argentina",
    "mexique", "mexico",
    "colombie", "colombia",
    "chili", "chile",
    "perou", "peru",
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
    "donnees",
    "apprentissage automatique",
    "modele",
]
