import asyncio
from typing import Iterator
import logging
import os
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_
from PropertyProspector.models.models import PropertyListing
from PropertyProspector.core.database import Listing, Base
from pydoll.constants import By
from pydoll.browser.page import Page
from dotenv import load_dotenv

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

# Database Configuration (PostgreSQL)
DATABASE_USER = os.getenv("POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DATABASE_HOST = os.getenv("POSTGRES_HOST")
DATABASE_PORT = os.getenv("POSTGRES_PORT")
DATABASE_NAME = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
# Ensure tables are created
Base.metadata.create_all(engine)


class BaseScraper(ABC):
    @abstractmethod
    def pages_to_scrape(self) -> Iterator[str]:
        pass

    @abstractmethod
    async def scrape(self, url: str) -> str:
        pass

    @abstractmethod
    async def parse(self, raw_data: str) -> List[PropertyListing]:
        pass

    # TODO - Explicit the ones that changed price
    def upload(self, listings: List[PropertyListing]) -> None:
        session = Session()
        added_count = 0
        edited_count = 0

        for listing in listings:
            existing_listing = (
                session.query(Listing)
                .filter(
                    and_(
                        Listing.property_id == listing.property_id,
                        Listing.platform == listing.platform
                    )
                )
                .first()
            )
            if existing_listing:
                for key, value in listing.model_dump(exclude_unset=True).items():
                    setattr(
                        existing_listing,
                        key,
                        value
                        if (value := getattr(listing, key)) is not None
                        else getattr(existing_listing, key),
                    )
                edited_count += 1
            else:
                db_listing = Listing(**listing.model_dump(exclude_unset=True))
                session.add(db_listing)
                added_count += 1

        session.commit()
        session.close()
        _logger.info(f"{added_count} items added.")
        _logger.info(f"{edited_count} items edited.")

    async def run(self):
        for url in self.pages_to_scrape():
            _logger.info(f"Scraping URL: {url}")
            raw_data = await self.scrape(url)
            if not raw_data:
                break
            if not (listings := await self.parse(raw_data)):
                _logger.info(f"No listings found at {url}. Ending pagination.")
                break

            self.upload(listings)

    async def is_cloudflare_blocked(self, page: Page) -> bool:
        return bool(
            await page.wait_element(
                By.XPATH,
                '//*[contains(text(), "Verify you are human")]',
                timeout=3,
                raise_exc=False,
            )
        )

    async def bypass_cloudflare(self, page: Page):
        cf_frame = await page.find_element(
            By.XPATH, "/html/body/div[1]/div/div[1]/div/div"
        )
        await page.execute_script(
            'argument.style = "width: 300px; height: 65px;"', cf_frame
        )
        await asyncio.sleep(1)
        await cf_frame.click()
