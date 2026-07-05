from __future__ import annotations

from app.db.models import BidClassification
from app.db.session import SessionLocal
from app.services.bid_classification_service import BidClassificationService


def run_bid_classification_post_activity(
    bid_ids: list[int] | None = None,
) -> list[BidClassification]:
    db = SessionLocal()
    try:
        service = BidClassificationService(db)
        results = service.classify_bids(bid_ids=bid_ids)

        print(
            {
                "stage": "post_classification",
                "classified_count": len(results),
            }
        )

        for row in results:
            print(
                {
                    "bid_id": row.bid_id,
                    "classification_id": row.id,
                    "is_relevant": row.is_relevant,
                    "reason": row.relevance_reason,
                }
            )

        return results
    finally:
        db.close()
