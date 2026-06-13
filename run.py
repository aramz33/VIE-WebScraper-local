import argparse
import re
from pathlib import Path

import pandas as pd

_ILLEGAL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

from config import OUTPUT_DIR
from filters import filter_offers
from profiles import PROFILES
from scraper import scrape_all_offers

CSV_COLUMNS: list[str] = [
    "applied", "score", "matched_keywords", "title", "company",
    "country", "city", "duration", "start_date", "posted_date",
    "expiry_date", "url", "description",
]


def _load_applied_urls(csv_path: Path) -> dict[str, str]:
    if not csv_path.exists():
        return {}
    df = pd.read_csv(csv_path, encoding="utf-8", dtype=str)
    if "applied" not in df.columns:
        return {}
    mask = df["applied"].notna() & (df["applied"].str.strip() != "")
    return dict(zip(df.loc[mask, "url"], df.loc[mask, "applied"]))


def _load_applied_rows(csv_path: Path, applied_urls: set[str]) -> list[dict]:
    if not csv_path.exists():
        return []
    df = pd.read_csv(csv_path, encoding="utf-8", dtype=str)
    mask = df["url"].isin(applied_urls)
    return df[mask].to_dict("records")


def _normalize_keywords(offers: list[dict]) -> list[dict]:
    result = []
    for o in offers:
        kw = o.get("matched_keywords", [])
        result.append({**o, "matched_keywords": ", ".join(kw) if isinstance(kw, list) else (kw or "")})
    return result


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

    csv_file = output_dir / "offres.csv"
    xlsx_file = output_dir / "offres.xlsx"

    applied_urls = _load_applied_urls(csv_file)
    applied_rows = _load_applied_rows(csv_file, set(applied_urls))
    fresh_urls = {o["url"] for o in filtered}

    filtered = [{**o, "applied": applied_urls.get(o["url"], "")} for o in filtered]

    expired_applied = [r for r in applied_rows if r["url"] not in fresh_urls]

    unapplied = sorted(
        [o for o in filtered if not o["applied"]],
        key=lambda o: o["score"],
        reverse=True,
    )
    still_active_applied = sorted(
        [o for o in filtered if o["applied"]],
        key=lambda o: o["score"],
        reverse=True,
    )
    expired = sorted(
        expired_applied,
        key=lambda o: float(o.get("score") or 0),
        reverse=True,
    )

    all_offers = _normalize_keywords(unapplied + still_active_applied + expired)

    df = pd.DataFrame(all_offers, columns=CSV_COLUMNS)

    df.to_csv(csv_file, index=False, encoding="utf-8")
    print(f"  → Saved to {csv_file}")

    df_clean = df.apply(
        lambda col: col.map(lambda v: _ILLEGAL_CHARS_RE.sub("", v) if isinstance(v, str) else v)
        if col.dtype == object else col
    )
    df_clean.to_excel(xlsx_file, index=False, engine="openpyxl")
    print(f"  → Saved to {xlsx_file}")


if __name__ == "__main__":
    main()
