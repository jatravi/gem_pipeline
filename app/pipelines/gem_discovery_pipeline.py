from __future__ import annotations

from app.pipelines.gem_llm_pipeline import run_llm_extraction_pipeline

from app.pipelines.gem_content_hash_pipeline import (
    run_content_hash_gate_pipeline,
)
from app.pipelines.gem_document_pipeline import (
    run_document_download_pipeline,
    run_document_text_extraction_pipeline,
)
from app.pipelines.gem_filter_pipeline import (
    run_keyword_prefilter_pipeline,
)


def run_gem_discovery_pipeline(
    limit: int = 20,
) -> None:
    """
    Complete GeM discovery pipeline.

    Pipeline Flow
    -------------
    1. Discover bids
    2. Keyword prefilter
    3. Download documents
    4. Extract text
    5. Content hash gate
    """

    print("=" * 70)
    print("STEP 1 : Bid Discovery")
    print("=" * 70)

    #
    # Existing discovery logic
    #

    print("Bid discovery completed.")
    print()

    print("=" * 70)
    print("STEP 2 : Keyword Prefilter")
    print("=" * 70)

    candidates = run_keyword_prefilter_pipeline(limit=limit)

    print()

    print("=" * 70)
    print("STEP 3 : Document Download")
    print("=" * 70)

    downloaded_documents = run_document_download_pipeline(
        candidates
    )

    print()

    print("=" * 70)
    print("STEP 4 : Text Extraction")
    print("=" * 70)

    processed_documents = (
        run_document_text_extraction_pipeline(
            downloaded_documents
        )
    )

    print()

    print("=" * 70)
    print("STEP 5 : Content Hash Gate")
    print("=" * 70)

    llm_candidates = run_content_hash_gate_pipeline(
        processed_documents
    )

    print()
    print(f"LLM Candidates : {len(llm_candidates)}")

    print()
    print("=" * 70)
    print("STEP 6 : LLM Extraction")
    print("=" * 70)

    extractions = run_llm_extraction_pipeline(llm_candidates)

    print()
    print("=" * 70)
    print("Pipeline Finished")
    print("=" * 70)