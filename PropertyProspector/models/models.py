from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
from decimal import Decimal


class PropertyListing(BaseModel):
    platform: str
    platform_id: str
    description: str
    price: Optional[Decimal]
    condo_fee: Optional[Decimal]
    location: Optional[str]
    address: Optional[str]
    url: Optional[str]
    area: Optional[Decimal] = None
    rooms: Optional[Decimal] = None
    bathrooms: Optional[Decimal] = None
    scraped_at: datetime = datetime.now(timezone(timedelta(hours=-3)))
