from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models import BidDocument, BidExtraction
from app.llm.client import BaseLLMExtractor, get_llm_extractor
from app.repositories.bid_extraction_repository import BidExtractionRepository


class DocumentExtractionService:
    def __init__(
        self,
        db: Session,
        extractor: BaseLLMExtractor | None = None,
    ) -> None:
        self.db = db
        self.extractor = extractor or get_llm_extractor()
        self.repository = BidExtractionRepository(db)

    def extract_document(
        self,
        document: BidDocument,
    ) -> BidExtraction:
        if not document.cleaned_text:
            raise ValueError(f"Document {document.id} has no cleaned text.")

        extraction = self.extractor.extract_tender_details(document.cleaned_text)

        bid_extraction = self.repository.create_extraction(
            bid_id=document.bid_id,
            extraction_version="v1",
            title=extraction.tender_title,
            scope=extraction.scope_of_work,
            value_inr=None,
            emd_inr=extraction.earnest_money_deposit,
            min_turnover_inr=None,
            experience_years=None,
            published_date=None,
            prebid_date=None,
            close_date=extraction.bid_submission_deadline,
            ministry=None,
            department=None,
            organisation=extraction.issuing_organization,
            office=None,
            relevant=True,
            relevance_reason="LLM extraction completed.",
            confidence=Decimal("1.0000"),
            prompt_version="v1",
            input_tokens=None,
            output_tokens=None,
            cost_inr=None,
            raw_response_json=extraction.model_dump(),
        )

        self.db.commit()
        self.db.refresh(bid_extraction)

        return bid_extraction

    def extract_documents(
        self,
        documents: list[BidDocument],
    ) -> list[BidExtraction]:
        results: list[BidExtraction] = []

        for document in documents:
            try:
                extraction = self.extract_document(document)
                results.append(extraction)

                print(
                    {
                        "document_id": document.id,
                        "bid_id": document.bid_id,
                        "extraction_id": extraction.id,
                    }
                )

            except Exception as exc:
                print(
                    {
                        "document_id": document.id,
                        "error": str(exc),
                    }
                )

        return results