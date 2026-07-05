from pathlib import Path

from app.pipelines.gem_document_pipeline import (
    run_document_download_pipeline,
    run_document_text_extraction_pipeline,
)
from app.pipelines.gem_filter_pipeline import (
    run_keyword_prefilter_pipeline,
)


def main() -> None:
    candidates = run_keyword_prefilter_pipeline(limit=20)

    if not candidates:
        print("No candidate bids found.")
        return

    downloaded_documents = run_document_download_pipeline(candidates)

    run_document_text_extraction_pipeline(downloaded_documents)


if __name__ == "__main__":
    main()
