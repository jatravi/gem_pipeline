from __future__ import annotations

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

    run_document_download_pipeline(candidates)

    print()

    print("=" * 70)
    print("STEP 4 : Text Extraction")
    print("=" * 70)

    run_document_text_extraction_pipeline()

    print()

    print("=" * 70)
    print("Pipeline Finished")
    print("=" * 70)