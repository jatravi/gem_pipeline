from sqlalchemy.orm import Session

from app.db.models import BidEvent


class BidEventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_event(
        self,
        bid_id: int,
        event_type: str,
        event_details: dict | None = None,
        pipeline_run_id: int | None = None,
    ) -> BidEvent:
        event = BidEvent(
            bid_id=bid_id,
            event_type=event_type,
            event_details=event_details,
            pipeline_run_id=pipeline_run_id,
        )
        self.db.add(event)
        self.db.flush()
        return event