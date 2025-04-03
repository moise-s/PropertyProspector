import logging
import asyncio
from decimal import Decimal
from typing import Iterator, List, Optional
from bs4 import BeautifulSoup
from PropertyProspector.core.scraper import BaseScraper
from PropertyProspector.models.models import PropertyListing, ScrapeSource
from pydoll.browser.chrome import Chrome

from PropertyProspector.utils.parser import extract_numeric_field, get_text

_logger = logging.getLogger(__name__)

# Silence INFO level logs from pydoll
logging.getLogger("pydoll.connection.connection").setLevel(logging.WARNING)


class ImovelWebScraper(BaseScraper):
    BASE_URL = (
        "https://www.imovelweb.com.br/apartamentos-venda-trindade-florianopolis-itacorubi-corrego-grande-"
        "carvoeira-pantanal-florianopolis-santa-monica-florianopolis-coqueiros-florianopolis-estreito-florianopolis-"
        "abraao-capoeiras-florianopolis-kobrasol-campinas-sao-jose-desde-2-ate-3-quartos-200000-1000000-reales"
    )

    def pages_to_scrape(self) -> Iterator[str]:
        page = 1
        while True:
            yield f"{self.BASE_URL}-pagina-{page}.html"
            page += 1

    async def scrape(self, url: str) -> Optional[str]:
        _logger.info(f"Scraping URL: {url}")
        async with Chrome() as browser:
            await browser.start()
            page = await browser.get_page()
            await page.go_to(url)
            await page._wait_page_load()
            MAX_RETRIES = 5
            for i in range(MAX_RETRIES):
                await page._wait_page_load()
                page_html = await page.page_source
                if "<title>Just a moment...<" in page_html:
                    _logger.info(
                        f"Got a cloudflare, attempt {i + 1}/{MAX_RETRIES}, waiting for its own handling!"
                    )
                    await asyncio.sleep(5)
                    await page._wait_page_load()
                    page_html = await page.page_source
                    if await self.is_cloudflare_blocked(page):
                        await self.bypass_cloudflare(page)
                        await asyncio.sleep(5)
                        continue
                    else:
                        break
                else:
                    break
            await page._wait_page_load()
            if "<title>Just a moment...<" in page_html:
                _logger.error(
                    f"Failed to bypass Cloudflare after {MAX_RETRIES} attempts for URL: {url}"
                )
                return None
            if (
                "Neste momento não temos imóveis com o perfil que está procurando"
                in page_html
            ):
                _logger.info("No more pages to scrape!")
                return None
            return page_html

    # TODO - Why scraped_at is not updated?
    async def parse(self, raw_html: str) -> List[PropertyListing]:
        soup = BeautifulSoup(raw_html, "html.parser")
        base_url = "https://www.imovelweb.com.br"
        listings = []

        for card in soup.select("div.postingsList-module__card-container"):
            layout = card.find(
                "div", class_="postingCardLayout-module__posting-card-layout"
            )
            property_id = layout.get("data-id")
            url_suffix = layout.get("data-to-posting", "")
            full_url = f"{base_url}{url_suffix}"

            # Price: remove currency symbol, thousand separators, and adjust decimals
            if price_elem := card.find("div", {"data-qa": "POSTING_CARD_PRICE"}):
                price_text = (
                    price_elem.text.strip()
                    .replace("R$", "")
                    .replace(".", "")
                    .replace(",", ".")
                )
                price = Decimal(price_text)
            else:
                price = None

            # Condo fee: extract number (with thousand separator) and remove dots
            condo_fee = extract_numeric_field(
                card,
                "div",
                r"([\d\.]+) Condominio",
                float,
                transform_func=lambda s: s.replace(".", ""),
                default=None,
            )

            location = get_text(card.find("h2", {"data-qa": "POSTING_CARD_LOCATION"}))
            address = get_text(
                card.find(
                    "div", class_="postingLocations-module__location-address-in-listing"
                )
            )
            total_area = extract_numeric_field(card, "span", r"(\d+) m²", float)
            rooms = extract_numeric_field(card, "span", r"(\d+) quartos", int)
            bathrooms = extract_numeric_field(card, "span", r"(\d+) ban", int)
            description = (
                get_text(card.find("h3", {"data-qa": "POSTING_CARD_DESCRIPTION"}))
                or "No description available."
            )

            listings.append(
                PropertyListing(
                    platform=ScrapeSource.IMOVELWEB,
                    property_id=property_id,
                    url=full_url,
                    description=description,
                    price=price,
                    condo_fee=condo_fee,
                    location=location,
                    address=address,
                    area=total_area,
                    rooms=rooms,
                    bathrooms=bathrooms,
                )
            )

        return listings
