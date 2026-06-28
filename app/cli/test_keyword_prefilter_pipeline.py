from app.pipelines.gem_filter_pipeline import run_keyword_prefilter_pipeline


def main() -> None:
    run_keyword_prefilter_pipeline(limit=20)


if __name__ == "__main__":
    main()