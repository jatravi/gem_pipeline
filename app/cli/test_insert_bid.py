from datetime import datetime

from app.db.models import Bid
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        bid = Bid(
            bid_number="GEM/TEST/B/0001",
            title="Test GeM Bid",
            ministry_name="Ministry of Testing",
            estimated_value=100000,
            emd_amount=5000,
            closing_date=datetime(2026, 6, 20, 12, 0, 0),
        )
        db.add(bid)
        db.commit()
        db.refresh(bid)
        print(f"Inserted bid id={bid.id}, bid_number={bid.bid_number}")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    main()
