import logging
import asyncio
from decimal import Decimal
from typing import Iterator, List, Optional
from bs4 import BeautifulSoup
from PropertyProspector.core.scraper import BaseScraper
from PropertyProspector.models.models import PropertyListing, ScrapeSource
from pydoll.browser.chrome import Chrome
from pydoll.constants import By
from PropertyProspector.utils.parser import (
    extract_numeric_by_data_cy,
    extract_numeric_field,
    get_clean_text,
)

_logger = logging.getLogger(__name__)

# Silence INFO level logs from pydoll
logging.getLogger("pydoll.connection.connection").setLevel(logging.WARNING)


class ZapImoveisScraper(BaseScraper):
    BASE_URL_INIT = "https://www.zapimoveis.com.br/venda/apartamentos/sc+florianopolis/2-quartos/?transacao=venda&onde=,Santa%20Catarina,Florian%C3%B3polis,,,,,city,BR%3ESanta%20Catarina%3ENULL%3EFlorianopolis,-27.594804,-48.556929,&tipos=apartamento_residencial&pagina="
    BASE_URL_END = (
        "&banheiros=1,2&quartos=2,3&vagas=1,2&precoMinimo=200000&precoMaximo=1000000"
    )

    def pages_to_scrape(self) -> Iterator[str]:
        page = 1
        while True:
            yield f"{self.BASE_URL_INIT}{page}{self.BASE_URL_END}"
            page += 1

    async def scrape(self, url: str) -> Optional[str]:
        _logger.info(f"Scraping URL: {url}")
        async with Chrome() as browser:
            await browser.start()
            page = await browser.get_page()
            await page.go_to(url)
            await page._wait_page_load()
            
            if "Não conseguimos encontrar a página solicitada" in await page.page_source:
                _logger.info("⚠️ No more pages to scrape!")
                return None

            max_scrolls = 30
            last_count = -1
            consecutive_same_count = 0
            for i in range(max_scrolls):
                page_html = await page.page_source
                soup = BeautifulSoup(page_html, "html.parser")
                cards = soup.select("div[data-position]")
                current_count = len(cards)
                _logger.info(f"[Scroll {i + 1}] Found total of {len(cards)} cards.")
                if current_count == last_count:
                    consecutive_same_count += 1
                    if consecutive_same_count >= 2:
                        _logger.info("✅ Full content loaded!")
                        break
                else:
                    consecutive_same_count = 0
                    last_count = current_count

                if cards:
                    last_card_position = max(
                        int(c["data-position"])
                        for c in cards
                        if c.get("data-position").isdigit()
                    )
                    selector = f'div[data-position="{last_card_position}"]'
                    try:
                        if last_card := await page.find_element(
                            By.CSS_SELECTOR, selector
                        ):
                            await last_card.scroll_into_view()
                            await asyncio.sleep(0.5)
                        else:
                            _logger.warning(
                                f"⚠️ Could not find element for data-position={last_card_position}"
                            )
                    except Exception as e:
                        _logger.warning(f"⚠️ Scroll error: {e}")
                else:
                    _logger.warning("⚠️ No cards found yet.")

                await asyncio.sleep(0.5)
        return page_html

    async def parse(self, raw_html: str) -> List[PropertyListing]:
        soup = BeautifulSoup(raw_html, "html.parser")
        listings = []

        for card in soup.select("div[data-position]"):
            if not (anchor := card.select_one("a.ListingCard_result-card__Pumtx")):
                continue

            full_url = anchor.get("href")
            property_id = anchor.get("data-id")

            price = extract_numeric_field(
                card,
                "p",
                r"([\d\.]+)",
                Decimal,
                transform_func=lambda s: s.replace(".", ""),
                default=None,
            )

            condo_fee = extract_numeric_field(
                card,
                "p",
                r"Cond\. R\$ ([\d\.]+)",
                Decimal,
                transform_func=lambda s: s.replace(".", ""),
                default=None,
            )

            location = get_clean_text(
                card.select_one('[data-cy="rp-cardProperty-location-txt"]')
            )
            address = get_clean_text(
                card.select_one('[data-cy="rp-cardProperty-street-txt"]')
            )

            total_area = extract_numeric_by_data_cy(
                card, "rp-cardProperty-propertyArea-txt", float
            )
            rooms = extract_numeric_by_data_cy(
                card, "rp-cardProperty-bedroomQuantity-txt", int
            )
            bathrooms = extract_numeric_by_data_cy(
                card, "rp-cardProperty-bathroomQuantity-txt", int
            )

            # Basic fallback description
            description = (
                f"{total_area} m², {rooms} quartos, {bathrooms} banheiros"
                if total_area and rooms and bathrooms
                else "No description available."
            )

            listings.append(
                PropertyListing(
                    platform=ScrapeSource.ZAP_IMOVEIS,
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
