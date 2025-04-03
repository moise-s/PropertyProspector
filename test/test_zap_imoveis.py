import os
import json
import pytest
from datetime import datetime
from PropertyProspector.websites.zap_imoveis import ZapImoveisScraper


def load_html(filename: str) -> str:
    with open(
        os.path.join(os.path.dirname(__file__), "html", filename), encoding="utf-8"
    ) as f:
        return f.read()


@pytest.mark.asyncio
async def test_parser(snapshot):
    html = load_html("zap_imoveis.html")
    listings = await ZapImoveisScraper().parse(html)

    for listing in listings:
        listing.scraped_at = datetime(2025, 1, 1)

    snapshot.assert_match(
        json.dumps(
            [item.model_dump() for item in listings],
            default=str,
            indent=2,
            ensure_ascii=False,
        ),
        "zap_imoveis.json",
    )
