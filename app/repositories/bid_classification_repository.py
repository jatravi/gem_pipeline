from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.db.models import BidClassification

class BidClassificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, classification_id: int) -> BidClassification | None:
        return (
            self.db.query(BidClassification)
            .filter(BidClassification.id == classification_id)
            .first()
        )

    def mark_previous_versions_not_current(self, bid_id: int) -> None:
        (
            self.db.query(BidClassification)
            .filter(
                BidClassification.bid_id == bid_id,
                BidClassification.is_current.is_(True),
            )
            .update(
                {
                    BidClassification.is_current: False,
                },
                synchronize_session=False,
            )
        )

    def create_classification(
        self,
        *,
        bid_id: int,
        company_profile_version: str | None,
        is_relevant: bool,
        relevance_reason: str | None,
        confidence: Decimal | None,
        raw_response_json: dict | None = None,
        classification_version: str = "v1",
        model_version: str = "v1",
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        cost_inr: Decimal | None = None,
    ) -> BidClassification:
        self.mark_previous_versions_not_current(bid_id)

        classification_label = "relevant" if is_relevant else "not_relevant"

        classification = BidClassification(
            bid_id=bid_id,
            company_profile_version=company_profile_version,
            classification_version=classification_version,
            is_current=True,
            classification_label=classification_label,
            relevance_score=confidence,
            eligibility_score=confidence,
            decision_reason=relevance_reason,
            model_version=model_version,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_inr=cost_inr,
            created_at=datetime.utcnow(),
        )

        # For compatibility with any direct dict/JSON serialization or dynamic usage:
        # We can store raw_response_json or extra info in python attributes if needed.
        # Note: the ORM model does not have raw_response_json, so we just set database fields.

        self.db.add(classification)
        self.db.flush()

        return classification
