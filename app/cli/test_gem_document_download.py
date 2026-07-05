from app.pipelines.gem_document_pipeline import (
    run_document_download_pipeline,
)
from app.pipelines.gem_filter_pipeline import (
    run_keyword_prefilter_pipeline,
)


def main() -> None:
    candidates = run_keyword_prefilter_pipeline(limit=20)

    if not candidates:
        print("No candidate bids found.")
        return

    run_document_download_pipeline(candidates)


if __name__ == "__main__":
    main()
