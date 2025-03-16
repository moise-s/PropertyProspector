import os
import json
import pytest
from datetime import datetime
from PropertyProspector.websites.imovel_web import ImovelWebScraper


def load_html(filename: str) -> str:
    with open(
        os.path.join(os.path.dirname(__file__), "html", filename), encoding="utf-8"
    ) as f:
        return f.read()


@pytest.mark.asyncio
async def test_scraper(snapshot):
    html = load_html("imovel_web.html")
    listings = await ImovelWebScraper().parse(html)

    for listing in listings:
        listing.scraped_at = datetime(2025, 1, 1)

    snapshot.assert_match(
        json.dumps(
            [item.model_dump() for item in listings],
            default=str,
            indent=2,
            ensure_ascii=False,
        ),
        "imovel_web.json",
    )
