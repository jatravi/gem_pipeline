from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.models import BidClassification
from app.repositories.bid_classification_repository import BidClassificationRepository
from app.repositories.bid_extraction_repository import BidExtractionRepository
from app.repositories.company_profile_repository import CompanyProfileRepository


class BidClassificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.classification_repo = BidClassificationRepository(db)
        self.extraction_repo = BidExtractionRepository(db)
        self.profile_repo = CompanyProfileRepository(db)

    def classify_bids(self, bid_ids: list[int] | None = None) -> list[BidClassification]:
        profile = self.profile_repo.get_active_profile()
        if not profile:
            raise ValueError("No active company profile found.")

        extractions = self.extraction_repo.get_latest_extractions_for_classification(bid_ids=bid_ids)

        results: list[BidClassification] = []

        for ex in extractions:
            text = " ".join(
                filter(
                    None,
                    [ex.title, ex.scope, ex.relevance_reason],
                )
            ).lower()

            score = 0
            preferred_hits = [k for k in (profile.preferred_keywords or []) if k.lower() in text]
            excluded_hits = [k for k in (profile.excluded_keywords or []) if k.lower() in text]

            score += len(preferred_hits)
            score -= 2 * len(excluded_hits)

            is_relevant = score > 0
            reason = (
                f"preferred={preferred_hits}, excluded={excluded_hits}, score={score}"
            )

            row = self.classification_repo.create_classification(
                bid_id=ex.bid_id,
                company_profile_version=profile.profile_version,
                is_relevant=is_relevant,
                relevance_reason=reason,
                confidence=Decimal("0.7000"),
                raw_response_json={
                    "preferred_hits": preferred_hits,
                    "excluded_hits": excluded_hits,
                    "score": score,
                },
            )
            results.append(row)

        self.db.commit()
        return results