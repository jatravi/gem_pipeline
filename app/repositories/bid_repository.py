from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Bid
from app.schemas.bid import ParsedBid


class BidRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_bid_number(self, bid_number: str) -> Bid | None:
        return self.db.query(Bid).filter(Bid.bid_number == bid_number).first()

    def upsert_from_parsed_bid(self, parsed_bid: ParsedBid) -> tuple[Bid, bool]:
        existing = self.get_by_bid_number(parsed_bid.bid_number)
        now = datetime.utcnow()

        if existing:
            existing.ra_number = parsed_bid.ra_number
            existing.title = parsed_bid.title
            existing.ministry = parsed_bid.ministry
            existing.department = parsed_bid.department
            existing.organisation = parsed_bid.organisation
            existing.office = parsed_bid.office
            existing.start_date = parsed_bid.start_date
            existing.closing_date = parsed_bid.closing_date
            existing.estimated_value = parsed_bid.estimated_value
            existing.emd_amount = parsed_bid.emd_amount
            existing.status = parsed_bid.status
            existing.source_url = parsed_bid.source_url
            existing.source_bid_id = parsed_bid.source_bid_id
            existing.parent_source_bid_id = parsed_bid.parent_source_bid_id
            existing.raw_listing_payload = parsed_bid.raw_listing_payload
            existing.last_seen_at = now
            existing.updated_at = now
            self.db.flush()
            return existing, False

        bid = Bid(
            bid_number=parsed_bid.bid_number,
            ra_number=parsed_bid.ra_number,
            title=parsed_bid.title,
            ministry=parsed_bid.ministry,
            department=parsed_bid.department,
            organisation=parsed_bid.organisation,
            office=parsed_bid.office,
            start_date=parsed_bid.start_date,
            closing_date=parsed_bid.closing_date,
            estimated_value=parsed_bid.estimated_value,
            emd_amount=parsed_bid.emd_amount,
            status=parsed_bid.status,
            source_url=parsed_bid.source_url,
            source_bid_id=parsed_bid.source_bid_id,
            parent_source_bid_id=parsed_bid.parent_source_bid_id,
            raw_listing_payload=parsed_bid.raw_listing_payload,
            first_seen_at=now,
            last_seen_at=now,
            created_at=now,
            updated_at=now,
        )
        self.db.add(bid)
        self.db.flush()
        return bid, True