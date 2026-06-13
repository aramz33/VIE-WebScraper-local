from __future__ import annotations

import argparse
import csv
import os
import smtplib
from datetime import date, datetime
from email.message import EmailMessage
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

MAX_OFFERS = 20
PARIS_TZ = ZoneInfo("Europe/Paris")
SUBJECT_PREFIX = "VIE Offers"
EMAIL_COLUMNS = (
    "score",
    "title",
    "company",
    "country",
    "city",
    "duration",
    "start_date",
    "url",
)


def _paris_today() -> date:
    return datetime.now(PARIS_TZ).date()


def _is_blank(value: str | None) -> bool:
    return not (value or "").strip()


def load_unapplied_offers(profile: str, base_dir: Path = Path("output"), limit: int = MAX_OFFERS) -> list[dict[str, str]]:
    csv_path = base_dir / profile / "offres.csv"
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return []

    with csv_path.open(newline="", encoding="utf-8") as fh:
        rows = [
            row
            for row in csv.DictReader(fh)
            if _is_blank(row.get("applied"))
        ]

    return rows[:limit]


def _profile_label(profile: str) -> str:
    return profile.strip().title() if profile.strip() else "Default"


def _subject(profile: str, today: date) -> str:
    return f"{SUBJECT_PREFIX} — {_profile_label(profile)} — {today.isoformat()}"


def _plain_body(rows: list[dict[str, str]], today: date) -> str:
    if not rows:
        return f"No new matching VIE offers today.\n\nDate: {today.isoformat()}\n"

    lines = [f"{len(rows)} new matching VIE offers as of {today.isoformat()}:", ""]
    for row in rows:
        title = row.get("title", "").strip() or "(untitled)"
        company = row.get("company", "").strip()
        country = row.get("country", "").strip()
        city = row.get("city", "").strip()
        score = row.get("score", "").strip()
        url = row.get("url", "").strip()
        location = ", ".join(part for part in (city, country) if part)
        meta = " | ".join(part for part in (company, location, f"score {score}" if score else "") if part)
        lines.append(f"- {title}" + (f" ({meta})" if meta else ""))
        if url:
            lines.append(f"  {url}")
    lines.append("")
    return "\n".join(lines)


def _html_body(rows: list[dict[str, str]], today: date) -> str:
    if not rows:
        return (
            "<!doctype html>"
            "<html><body>"
            f"<p>No new matching VIE offers today.</p>"
            f"<p>Date: {escape(today.isoformat())}</p>"
            "</body></html>"
        )

    header_cells = "".join(f"<th>{escape(column.replace('_', ' ').title())}</th>" for column in EMAIL_COLUMNS)
    body_rows = []

    for row in rows:
        cells = []
        for column in EMAIL_COLUMNS:
            value = (row.get(column) or "").strip()
            if column == "url" and value:
                safe_url = escape(value, quote=True)
                cells.append(f'<td><a href="{safe_url}">Open offer</a></td>')
            else:
                cells.append(f"<td>{escape(value)}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    return (
        "<!doctype html>"
        "<html><body>"
        f"<p>{len(rows)} new matching VIE offers as of {escape(today.isoformat())}.</p>"
        '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">'
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
        "</body></html>"
    )


def build_message(profile: str, to_addr: str, from_addr: str, rows: list[dict[str, str]], today: date | None = None) -> EmailMessage:
    message_date = today or _paris_today()
    msg = EmailMessage()
    msg["Subject"] = _subject(profile, message_date)
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(_plain_body(rows, message_date))
    msg.add_alternative(_html_body(rows, message_date), subtype="html")
    return msg


def send_message(msg: EmailMessage, username: str, app_password: str) -> None:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(username, app_password)
        smtp.send_message(msg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Email VIE scraper results.")
    parser.add_argument("--profile", default="adam")
    parser.add_argument("--to", required=True)
    args = parser.parse_args()

    username = os.environ.get("MAIL_USERNAME")
    app_password = os.environ.get("MAIL_APP_PASSWORD")
    if not username or not app_password:
        raise SystemExit("MAIL_USERNAME and MAIL_APP_PASSWORD must be set.")

    rows = load_unapplied_offers(args.profile)
    msg = build_message(args.profile, args.to, username, rows)
    send_message(msg, username, app_password)


if __name__ == "__main__":
    main()
