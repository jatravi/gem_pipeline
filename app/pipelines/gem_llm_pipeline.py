from __future__ import annotations

from app.db.models import BidDocument, BidExtraction
from app.db.session import SessionLocal
from app.services.document_extraction_service import DocumentExtractionService


def run_llm_extraction_pipeline(
    documents: list[BidDocument],
) -> list[BidExtraction]:
    """
    Execute LLM extraction for all documents that survived
    the cheap filtering stages.
    """

    db = SessionLocal()

    try:
        extraction_service = DocumentExtractionService(db)

        extractions: list[BidExtraction] = []

        for document in documents:

            try:
                extraction = extraction_service.extract_document(document)

                extractions.append(extraction)

                print(
                    {
                        "document_id": document.id,
                        "bid_id": document.bid_id,
                        "extraction_id": extraction.id,
                        "title": extraction.title,
                    }
                )

            except Exception as exc:

                print(
                    {
                        "document_id": document.id,
                        "status": "failed",
                        "error": str(exc),
                    }
                )

        return extractions

    finally:
        db.close()