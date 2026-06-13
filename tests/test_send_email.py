from datetime import date

from send_email import build_message, load_unapplied_offers


def test_load_unapplied_offers_returns_top_unapplied_rows(tmp_path):
    csv_dir = tmp_path / "adam"
    csv_dir.mkdir()
    (csv_dir / "offres.csv").write_text(
        "applied,score,title,company,country,city,duration,start_date,url\n"
        ",10,Best Offer,Acme,Singapour,Singapore,12,2026-07-01,https://example.com/1\n"
        "yes,9,Already Applied,Acme,Japon,Tokyo,24,2026-08-01,https://example.com/2\n"
        ",8,Second Offer,Beta,Chine,Shanghai,18,2026-09-01,https://example.com/3\n",
        encoding="utf-8",
    )

    rows = load_unapplied_offers("adam", base_dir=tmp_path, limit=1)

    assert len(rows) == 1
    assert rows[0]["title"] == "Best Offer"


def test_load_unapplied_offers_missing_csv_returns_empty_list(tmp_path):
    assert load_unapplied_offers("adam", base_dir=tmp_path) == []


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
    )

    plain = msg.get_body(("plain",)).get_content()
    html = msg.get_body(("html",)).get_content()

    assert "1 new matching VIE offers as of 2026-06-13" in plain
    assert "AI Engineer" in plain
    assert "Acme &amp; Sons" in html
    assert 'href="https://example.com/offers/1?x=1&amp;y=2"' in html
    assert "Open offer" in html
