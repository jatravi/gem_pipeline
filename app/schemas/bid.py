from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class ParsedBid(BaseModel):
    bid_number: str
    ra_number: str | None = None
    title: str | None = None
    ministry: str | None = None
    department: str | None = None
    organisation: str | None = None
    office: str | None = None
    start_date: datetime | None = None
    closing_date: datetime | None = None
    estimated_value: Decimal | None = None
    emd_amount: Decimal | None = None
    status: str | None = None
    source_url: str | None = None
    source_bid_id: str | None = None
    parent_source_bid_id: str | None = None
    raw_listing_payload: dict | None = None
