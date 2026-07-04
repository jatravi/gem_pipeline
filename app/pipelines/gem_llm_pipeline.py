from __future__ import annotations
from decimal import Decimal

from app.db.models import BidDocument, BidExtraction
from app.db.session import SessionLocal
from app.services.document_extraction_service import DocumentExtractionService


def run_llm_extraction_pipeline(
    documents: list[BidDocument],
) -> tuple[list[BidExtraction], dict]:
    """
    Runs the LLM extraction stage for a list of candidate documents.
    Returns a tuple of (extractions, summary_stats).
    """
    db = SessionLocal()

    extractions: list[BidExtraction] = []
    llm_success = 0
    llm_failed = 0
    llm_fallback_used = 0
    llm_estimated_cost_inr = Decimal("0")

    try:
        extraction_service = DocumentExtractionService(db)

        for document in documents:
            try:
                extraction = extraction_service.extract_document(document)
                extractions.append(extraction)
                llm_success += 1

                # Check if fallback was used via raw_response_json
                raw_resp = extraction.raw_response_json or {}
                usage_block = raw_resp.get("usage", {})
                if usage_block.get("fallback_used", False):
                    llm_fallback_used += 1

                if extraction.cost_inr:
                    llm_estimated_cost_inr += extraction.cost_inr

                print(
                    {
                        "document_id": document.id,
                        "bid_id": document.bid_id,
                        "extraction_id": extraction.id,
                        "title": extraction.title,
                        "fallback_used": usage_block.get("fallback_used", False),
                        "cost_inr": str(extraction.cost_inr or 0),
                    }
                )

            except Exception as exc:
                llm_failed += 1
                print(
                    {
                        "document_id": document.id,
                        "status": "failed",
                        "error": str(exc),
                    }
                )

        summary = {
            "llm_success": llm_success,
            "llm_failed": llm_failed,
            "llm_fallback_used": llm_fallback_used,
            "llm_estimated_cost_inr": llm_estimated_cost_inr,
        }
        return extractions, summary

    finally:
        db.close()