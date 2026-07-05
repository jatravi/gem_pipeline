from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import BidExtraction


class BidExtractionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(
        self,
        extraction_id: int,
    ) -> BidExtraction | None:
        return (
            self.db.query(BidExtraction)
            .filter(BidExtraction.id == extraction_id)
            .first()
        )

    def get_current_extraction(
        self,
        bid_id: int,
    ) -> BidExtraction | None:
        return (
            self.db.query(BidExtraction)
            .filter(
                BidExtraction.bid_id == bid_id,
                BidExtraction.is_current.is_(True),
            )
            .first()
        )

    def get_latest_extraction(
        self,
        bid_id: int,
    ) -> BidExtraction | None:
        return (
            self.db.query(BidExtraction)
            .filter(
                BidExtraction.bid_id == bid_id,
            )
            .order_by(
                BidExtraction.created_at.desc(),
            )
            .first()
        )

    def mark_previous_versions_not_current(
        self,
        bid_id: int,
    ) -> None:
        (
            self.db.query(BidExtraction)
            .filter(
                BidExtraction.bid_id == bid_id,
                BidExtraction.is_current.is_(True),
            )
            .update(
                {
                    BidExtraction.is_current: False,
                },
                synchronize_session=False,
            )
        )

    def create_extraction(
        self,
        *,
        bid_id: int,
        extraction_version: str,
        title: str | None,
        scope: str | None,
        value_inr,
        emd_inr,
        min_turnover_inr,
        experience_years,
        published_date,
        prebid_date,
        close_date,
        ministry,
        department,
        organisation,
        office,
        relevant,
        relevance_reason,
        confidence,
        prompt_version: str | None,
        input_tokens,
        output_tokens,
        cost_inr,
        raw_response_json,
    ) -> BidExtraction:

        self.mark_previous_versions_not_current(bid_id)

        extraction = BidExtraction(
            bid_id=bid_id,
            extraction_version=extraction_version,
            is_current=True,
            title=title,
            scope=scope,
            value_inr=value_inr,
            emd_inr=emd_inr,
            min_turnover_inr=min_turnover_inr,
            experience_years=experience_years,
            published_date=published_date,
            prebid_date=prebid_date,
            close_date=close_date,
            ministry=ministry,
            department=department,
            organisation=organisation,
            office=office,
            relevant=relevant,
            relevance_reason=relevance_reason,
            confidence=confidence,
            prompt_version=prompt_version,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_inr=cost_inr,
            raw_response_json=raw_response_json,
            created_at=datetime.utcnow(),
        )

        self.db.add(extraction)
        self.db.flush()

        return extraction

    def delete_extraction(
        self,
        extraction_id: int,
    ) -> bool:

        extraction = self.get_by_id(extraction_id)

        if extraction is None:
            return False

        self.db.delete(extraction)
        self.db.flush()

        return True

    def get_latest_extractions_for_classification(
        self,
        bid_ids: list[int] | None = None,
    ) -> list[BidExtraction]:

        query = self.db.query(BidExtraction).filter(BidExtraction.is_current.is_(True))

        if bid_ids:
            query = query.filter(BidExtraction.bid_id.in_(bid_ids))

        return query.all()
