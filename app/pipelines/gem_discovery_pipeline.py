from __future__ import annotations
from decimal import Decimal

from app.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.sources.gem.discovery import GeMDiscoveryRunner
from app.pipelines.gem_filter_pipeline import run_keyword_prefilter_pipeline
from app.pipelines.gem_document_pipeline import (
    run_document_download_pipeline,
    run_document_text_extraction_pipeline,
)
from app.pipelines.gem_content_hash_pipeline import run_content_hash_gate_pipeline
from app.pipelines.gem_llm_pipeline import run_llm_extraction_pipeline
from app.pipelines.post_classification_pipeline import (
    run_bid_classification_post_activity,
)
from app.llm.client import check_ollama_health


def run_gem_pipeline(limit: int = 20) -> dict:
    """
    Canonical single entrypoint for the GeM Tender Discovery & Extraction Pipeline.
    Runs all stages sequentially and returns a machine-readable summary.
    """
    # 1. Run database initialization and alignment (non-destructive)
    print("Initializing database schema and seeding active profile...")
    init_db()

    # 2. Ollama health check if Ollama is selected
    if settings.LLM_PROVIDER.strip().lower() == "ollama":
        print("Performing Ollama health check...")
        check_ollama_health()
        print("Ollama health check passed.")

    print("=" * 70)
    print("STAGE 1 : Bid Discovery")
    print("=" * 70)
    db = SessionLocal()
    try:
        runner = GeMDiscoveryRunner(db)
        discovery_result = runner.run()
        bids_discovered = discovery_result.get("bids_discovered", 0)
        print(f"Discovery complete: {discovery_result}")
    except Exception as exc:
        print(f"Fatal error during discovery initialization: {exc}")
        raise exc
    finally:
        db.close()

    print()
    print("=" * 70)
    print("STAGE 2 : Keyword Prefilter")
    print("=" * 70)
    candidates = run_keyword_prefilter_pipeline(limit=limit)
    bids_scanned = bids_discovered  # Bids evaluated from recent run
    bids_relevant = len(candidates)

    print()
    print("=" * 70)
    print("STAGE 3 : Document Download")
    print("=" * 70)
    downloaded_documents = run_document_download_pipeline(candidates)
    documents_downloaded = len(downloaded_documents)

    print()
    print("=" * 70)
    print("STAGE 4 : Text Extraction")
    print("=" * 70)
    processed_documents = run_document_text_extraction_pipeline(downloaded_documents)
    documents_processed = len(processed_documents)
    documents_failed_text_extraction = documents_downloaded - documents_processed

    print()
    print("=" * 70)
    print("STAGE 5 : Content Hash Gate")
    print("=" * 70)
    llm_candidates = run_content_hash_gate_pipeline(processed_documents)
    llm_candidates_count = len(llm_candidates)

    print()
    print("=" * 70)
    print("STAGE 6 : LLM Extraction")
    print("=" * 70)
    extractions, llm_summary = run_llm_extraction_pipeline(llm_candidates)
    # llm_summary = {
    #     "llm_success": len(extractions),
    #     "llm_failed": len(llm_candidates) - len(extractions),
    #     "llm_fallback_used": 0,
    #     "llm_estimated_cost_inr": Decimal("0"),
    # }

    print()
    print("=" * 70)
    print("STAGE 7 : Bid Classification")
    print("=" * 70)
    successful_bid_ids = []

    for ex in extractions:
        successful_bid_ids.append(ex.bid_id)
    if successful_bid_ids:
        classifications = run_bid_classification_post_activity(
            bid_ids=successful_bid_ids
        )
        print(f"Classified {len(classifications)} bids.")
    else:
        print("No successful extractions to classify.")

    # Compile the final summary
    summary = {
        "bids_scanned": bids_scanned,
        "bids_relevant": bids_relevant,
        "documents_downloaded": documents_downloaded,
        "documents_processed": documents_processed,
        "documents_failed_text_extraction": documents_failed_text_extraction,
        "llm_candidates": llm_candidates_count,
        "llm_success": llm_summary["llm_success"],
        "llm_failed": llm_summary["llm_failed"],
        "llm_fallback_used": llm_summary["llm_fallback_used"],
        "llm_estimated_cost_inr": llm_summary["llm_estimated_cost_inr"],
        "run_status": "success",
    }

    print()
    print("=" * 70)
    print("PIPELINE RUN SUMMARY")
    print("=" * 70)
    # Output machine-readable summary dict to stdout once
    print(summary)
    print("=" * 70)

    return summary


def run_gem_discovery_pipeline(limit: int = 20) -> None:
    """
    Backward-compatible wrapper for run_gem_pipeline.
    """
    run_gem_pipeline(limit=limit)
