import logging
import os
from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from PropertyProspector.models.models import PropertyListing
from PropertyProspector.core.database import Listing, Base

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


DATABASE_PATH = "db/database.db"
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
engine = create_engine(f"sqlite:///{DATABASE_PATH}")
Session = sessionmaker(bind=engine)
# Ensure tables are created
Base.metadata.create_all(engine)


class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self) -> str:
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
                .filter_by(platform_id=listing.platform_id)
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
        raw_data = await self.scrape()
        listings = await self.parse(raw_data)
        self.upload(listings)
