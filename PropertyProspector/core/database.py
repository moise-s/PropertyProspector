from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, DateTime

Base = declarative_base()


class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_id = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Numeric(precision=12, scale=2), nullable=True)
    condo_fee = Column(Numeric(precision=12, scale=2), nullable=True)
    location = Column(String, nullable=True)
    address = Column(String, nullable=True)
    url = Column(String, nullable=True)
    area = Column(Numeric(precision=10, scale=2), nullable=True)
    rooms = Column(Numeric(precision=4, scale=1), nullable=True)
    bathrooms = Column(Numeric(precision=4, scale=1), nullable=True)
    scraped_at = Column(
        DateTime, nullable=False, default=datetime.now(timezone(timedelta(hours=-3)))
    )
