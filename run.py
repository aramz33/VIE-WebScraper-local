import argparse
from datetime import date

import pandas as pd

from config import OUTPUT_DIR
from filters import filter_offers
from profiles import PROFILES
from scraper import scrape_all_offers

CSV_COLUMNS: list[str] = [
    "score", "matched_keywords", "title", "company",
    "country", "city", "duration", "start_date", "posted_date", "expiry_date", "url", "description",
]


def _join_keywords(keywords: list[str]) -> str:
    return ", ".join(keywords)


def main() -> None:
    parser = argparse.ArgumentParser(description="VIE offer scraper")
    parser.add_argument(
        "--profile",
        default=None,
        help=f"Named profile ({', '.join(PROFILES)}). Omit to use default config.",
    )
    args = parser.parse_args()

    profile = None
    if args.profile is not None:
        if args.profile not in PROFILES:
            print(f"Unknown profile '{args.profile}'. Available: {', '.join(PROFILES)}")
            raise SystemExit(1)
        profile = PROFILES[args.profile]

    print("Scraping https://mon-vie-via.businessfrance.fr/offres...")
    try:
        raw_offers = scrape_all_offers()
    except Exception as exc:
        print(f"Scraping failed: {exc}")
        raise SystemExit(1)
    print(f"  → {len(raw_offers)} offers extracted")

    filtered = filter_offers(raw_offers, profile=profile)
    profile_label = profile.name if profile else "default"
    print(f"  → {len(filtered)} offers match profile '{profile_label}'")

    if not filtered:
        print("No matching offers found.")
        return

    output_dir = OUTPUT_DIR / profile.name if profile else OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(filtered, columns=CSV_COLUMNS)
    df["matched_keywords"] = df["matched_keywords"].apply(_join_keywords)

    filename_stem = f"offres_{date.today().isoformat()}"

    csv_file = output_dir / f"{filename_stem}.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8")
    print(f"  → Saved to {csv_file}")

    xlsx_file = output_dir / f"{filename_stem}.xlsx"
    df.to_excel(xlsx_file, index=False, engine="openpyxl")
    print(f"  → Saved to {xlsx_file}")


if __name__ == "__main__":
    main()
