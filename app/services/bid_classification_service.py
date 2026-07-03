from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import BidClassification, BidExtraction
from app.llm.classifier import FakeBidClassifier
from app.repositories.bid_classification_repository import (
    BidClassificationRepository,
)


class BidClassificationService:
    def __init__(
        self,
        db: Session,
        classifier: FakeBidClassifier | None = None,
    ) -> None:
        self.db = db
        self.classifier = classifier or FakeBidClassifier()
        self.repository = BidClassificationRepository(db)

    def classify_extraction(
        self,
        extraction: BidExtraction,
    ) -> BidClassification:

        result = self.classifier.classify(
            extraction=extraction,
        )

        classification = self.repository.create_classification(
            bid_id=extraction.bid_id,
            classification_version="v1",
            is_current=True,
            classification_label=result.classification_label,
            relevance_score=result.relevance_score,
            eligibility_score=result.eligibility_score,
            decision_reason=result.decision_reason,
            company_profile_version="v1",
            model_version="fake-llm-v1",
            input_tokens=None,
            output_tokens=None,
            cost_inr=None,
        )

        self.db.commit()
        self.db.refresh(classification)

        return classification

    def classify_extractions(
        self,
        extractions: list[BidExtraction],
    ) -> list[BidClassification]:

        results: list[BidClassification] = []

        for extraction in extractions:
            try:
                classification = self.classify_extraction(extraction)

                results.append(classification)

                print(
                    {
                        "extraction_id": extraction.id,
                        "bid_id": extraction.bid_id,
                        "classification_id": classification.id,
                        "classification": classification.classification_label,
                    }
                )

            except Exception as exc:
                print(
                    {
                        "extraction_id": extraction.id,
                        "error": str(exc),
                    }
                )

        return results