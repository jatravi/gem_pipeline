from sqlalchemy import select

from app.db.models import Bid, BidEvent
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        bid = db.execute(
            select(Bid).where(Bid.bid_number == "GEM/TEST/B/0001")
        ).scalar_one()

        event = BidEvent(
            bid_id=bid.id,
            event_type="DISCOVERED",
            event_details={"source": "manual_test", "note": "first insert from python"},
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        print(f"Inserted event id={event.id} for bid_id={event.bid_id}")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    main()
