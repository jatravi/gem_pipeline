from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ParsedBid(BaseModel):
    bid_number: str
    ra_number: Optional[str] = None
    title: Optional[str] = None
    ministry: Optional[str] = None
    department: Optional[str] = None
    organisation: Optional[str] = None
    office: Optional[str] = None
    start_date: Optional[datetime] = None
    closing_date: Optional[datetime] = None
    estimated_value: Optional[Decimal] = None
    emd_amount: Optional[Decimal] = None
    status: Optional[str] = None
    source_url: Optional[str] = None