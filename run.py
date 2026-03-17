import pandas as pd

from config import OUTPUT_DIR, get_output_file
from filters import filter_offers
from scraper import scrape_all_offers

CSV_COLUMNS = [
    "score", "matched_keywords", "title", "company",
    "country", "city", "duration", "start_date", "posted_date", "url", "description",
]


def main() -> None:
    print("Scraping https://mon-vie-via.businessfrance.fr/offres...")
    raw_offers = scrape_all_offers()
    print(f"  → {len(raw_offers)} offers extracted")

    filtered = filter_offers(raw_offers)
    print(f"  → {len(filtered)} offers match your profile")

    if not filtered:
        print("No matching offers found. Check your keywords or country list in config.py.")
        return

    output_file = get_output_file()
    OUTPUT_DIR.mkdir(exist_ok=True)
    df = pd.DataFrame(filtered, columns=CSV_COLUMNS)
    df["matched_keywords"] = df["matched_keywords"].apply(lambda kws: ", ".join(kws))
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"  → Saved to {output_file}")


if __name__ == "__main__":
    main()
