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

PARIS_TZ = ZoneInfo("Europe/Paris")
SUBJECT_PREFIX = "VIE Offers"
EMAIL_COLUMNS = (
    "posted_date",
    "score",
    "title",
    "company",
    "country",
    "city",
    "duration",
    "start_date",
    "url",
)
ATTACHMENTS = (
    ("offres.xlsx", "application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ("offres.csv", "text", "csv"),
)


def _paris_today() -> date:
    return datetime.now(PARIS_TZ).date()


def _posted_date(row: dict[str, str]) -> date:
    value = (row.get("posted_date") or "").strip()
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.min


def load_offers(profile: str, base_dir: Path = Path("output")) -> list[dict[str, str]]:
    csv_path = base_dir / profile / "offres.csv"
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return []

    with csv_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    return sorted(rows, key=_posted_date, reverse=True)


def output_attachments(profile: str, base_dir: Path = Path("output")) -> list[tuple[Path, str, str]]:
    output_dir = base_dir / profile
    return [
        (path, maintype, subtype)
        for filename, maintype, subtype in ATTACHMENTS
        if (path := output_dir / filename).exists()
    ]


def _profile_label(profile: str) -> str:
    return profile.strip().title() if profile.strip() else "Default"


def _subject(profile: str, today: date) -> str:
    return f"{SUBJECT_PREFIX} — {_profile_label(profile)} — {today.isoformat()}"


def _plain_body(rows: list[dict[str, str]], today: date) -> str:
    if not rows:
        return f"No new matching VIE offers today.\n\nDate: {today.isoformat()}\n"

    lines = [
        f"{len(rows)} matching VIE offers as of {today.isoformat()}, sorted by most recent posted date:",
        "",
    ]
    for row in rows:
        title = row.get("title", "").strip() or "(untitled)"
        company = row.get("company", "").strip()
        country = row.get("country", "").strip()
        city = row.get("city", "").strip()
        score = row.get("score", "").strip()
        posted_date = row.get("posted_date", "").strip()
        url = row.get("url", "").strip()
        location = ", ".join(part for part in (city, country) if part)
        meta = " | ".join(
            part
            for part in (posted_date, company, location, f"score {score}" if score else "")
            if part
        )
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
        f"<p>{len(rows)} matching VIE offers as of {escape(today.isoformat())}, "
        "sorted by most recent posted date.</p>"
        '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">'
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
        "</body></html>"
    )


def build_message(
    profile: str,
    to_addr: str,
    from_addr: str,
    rows: list[dict[str, str]],
    today: date | None = None,
    attachments: list[tuple[Path, str, str]] | None = None,
) -> EmailMessage:
    message_date = today or _paris_today()
    msg = EmailMessage()
    msg["Subject"] = _subject(profile, message_date)
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(_plain_body(rows, message_date))
    msg.add_alternative(_html_body(rows, message_date), subtype="html")

    for path, maintype, subtype in attachments or []:
        msg.add_attachment(
            path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )

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

    rows = load_offers(args.profile)
    msg = build_message(args.profile, args.to, username, rows, attachments=output_attachments(args.profile))
    send_message(msg, username, app_password)


if __name__ == "__main__":
    main()
