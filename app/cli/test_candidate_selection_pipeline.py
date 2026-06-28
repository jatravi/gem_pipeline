from dataclasses import asdict

from app.pipelines.gem_filter_pipeline import run_keyword_prefilter_pipeline


def main():
    results = run_keyword_prefilter_pipeline(limit=20)

    print("\nRelevant Candidates\n")

    for row in results:
        if row.is_relevant:
            print(asdict(row))


if __name__ == "__main__":
    main()