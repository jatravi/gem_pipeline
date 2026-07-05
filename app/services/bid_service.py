from sqlalchemy.orm import Session

from app.repositories.bid_repository import BidRepository


class BidService:
    def __init__(self, db: Session) -> None:
        self.bid_repository = BidRepository(db)

    def get_recent_bids(self, limit: int = 20):
        return self.bid_repository.get_recent_bids(limit)
