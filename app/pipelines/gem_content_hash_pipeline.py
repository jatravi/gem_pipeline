from __future__ import annotations

from app.db.models import BidDocument
from app.db.session import SessionLocal
from app.filters.content_hash_gate import should_skip_llm_due_to_same_text


def run_content_hash_gate_pipeline(
    documents: list[BidDocument],
) -> list[BidDocument]:
    """
    Compare processed document hashes and determine which
    documents should proceed to the LLM stage.
    """

    db = SessionLocal()

    try:
        llm_candidates: list[BidDocument] = []

        previous_hashes: dict[int, str] = {}

        for document in documents:

            document = db.merge(document)

            previous_hash = previous_hashes.get(document.bid_id)

            skip_llm = should_skip_llm_due_to_same_text(
                current_text_hash=document.text_hash,
                previous_text_hash=previous_hash,
            )

            print(
                {
                    "bid_id": document.bid_id,
                    "document_id": document.id,
                    "previous_hash": previous_hash,
                    "current_hash": document.text_hash,
                    "skip_llm": skip_llm,
                }
            )

            if not skip_llm:
                llm_candidates.append(document)

            previous_hashes[document.bid_id] = document.text_hash or ""

        return llm_candidates

    finally:
        db.close()
