from datetime import date

from send_email import build_message, load_offers, output_attachments


def test_load_offers_returns_all_rows_sorted_by_most_recent_posted_date(tmp_path):
    csv_dir = tmp_path / "adam"
    csv_dir.mkdir()
    (csv_dir / "offres.csv").write_text(
        "applied,score,title,company,country,city,duration,start_date,posted_date,url\n"
        ",10,Older Offer,Acme,Singapour,Singapore,12,2026-07-01,2026-06-10,https://example.com/1\n"
        "yes,9,Applied Newest,Acme,Japon,Tokyo,24,2026-08-01,2026-06-12,https://example.com/2\n"
        ",8,Middle Offer,Beta,Chine,Shanghai,18,2026-09-01,2026-06-11,https://example.com/3\n",
        encoding="utf-8",
    )

    rows = load_offers("adam", base_dir=tmp_path)

    assert [row["title"] for row in rows] == ["Applied Newest", "Middle Offer", "Older Offer"]


def test_load_offers_missing_csv_returns_empty_list(tmp_path):
    assert load_offers("adam", base_dir=tmp_path) == []


def test_output_attachments_returns_existing_result_files(tmp_path):
    csv_dir = tmp_path / "adam"
    csv_dir.mkdir()
    (csv_dir / "offres.csv").write_text("title\nOffer\n", encoding="utf-8")
    (csv_dir / "offres.xlsx").write_bytes(b"xlsx")

    attachments = output_attachments("adam", base_dir=tmp_path)

    assert [path.name for path, _, _ in attachments] == ["offres.xlsx", "offres.csv"]


def test_build_message_uses_required_subject_prefix_and_no_offer_copy():
    msg = build_message(
        "adam",
        "adam.ramsis.2@gmail.com",
        "sender@example.com",
        [],
        today=date(2026, 6, 13),
    )

    assert msg["Subject"] == "VIE Offers — Adam — 2026-06-13"
    assert "No new matching VIE offers today." in msg.get_body(("plain",)).get_content()
    assert "No new matching VIE offers today." in msg.get_body(("html",)).get_content()


def test_build_message_renders_clickable_html_table_and_plain_fallback():
    msg = build_message(
        "adam",
        "adam.ramsis.2@gmail.com",
        "sender@example.com",
        [{
            "posted_date": "2026-06-12",
            "score": "10",
            "title": "AI Engineer",
            "company": "Acme & Sons",
            "country": "Singapour",
            "city": "Singapore",
            "duration": "12",
            "start_date": "2026-07-01",
            "url": "https://example.com/offers/1?x=1&y=2",
        }],
        today=date(2026, 6, 13),
        attachments=[],
    )

    plain = msg.get_body(("plain",)).get_content()
    html = msg.get_body(("html",)).get_content()

    assert "1 matching VIE offers as of 2026-06-13" in plain
    assert "2026-06-12" in plain
    assert "AI Engineer" in plain
    assert "Posted Date" in html
    assert "Acme &amp; Sons" in html
    assert 'href="https://example.com/offers/1?x=1&amp;y=2"' in html
    assert "Open offer" in html


def test_build_message_adds_attachments(tmp_path):
    attachment = tmp_path / "offres.csv"
    attachment.write_text("title\nAI Engineer\n", encoding="utf-8")

    msg = build_message(
        "adam",
        "adam.ramsis.2@gmail.com",
        "sender@example.com",
        [],
        today=date(2026, 6, 13),
        attachments=[(attachment, "text", "csv")],
    )

    assert msg.get_payload()[-1].get_filename() == "offres.csv"
