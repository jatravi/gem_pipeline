from sqlalchemy.orm import Session

from app.repositories.bid_event_repository import BidEventRepository
from app.repositories.bid_repository import BidRepository
from app.schemas.bid import ParsedBid


class DiscoveryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.bid_repository = BidRepository(db)
        self.bid_event_repository = BidEventRepository(db)

    def save_discovered_bid(
        self,
        parsed_bid: ParsedBid,
        pipeline_run_id: int | None = None,
    ):
        try:
            bid, inserted = self.bid_repository.upsert_from_parsed_bid(parsed_bid)

            event_type = "DISCOVERED" if inserted else "UPDATED_FROM_LISTING"

            self.bid_event_repository.create_event(
                bid_id=bid.id,
                event_type=event_type,
                event_details={
                    "bid_number": parsed_bid.bid_number,
                    "ra_number": parsed_bid.ra_number,
                    "title": parsed_bid.title,
                    "status": parsed_bid.status,
                },
                pipeline_run_id=pipeline_run_id,
            )

            self.db.commit()
            self.db.refresh(bid)
            return bid, inserted

        except Exception:
            self.db.rollback()
            raise
