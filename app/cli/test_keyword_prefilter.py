from app.filters.keyword_prefilter import score_bid_text


def main() -> None:
    samples = [
        {
            "title": "Selection of agency for development of AI-enabled grievance redressal platform",
            "description": "Software development, implementation, cloud hosting, and support services",
        },
        {
            "title": "Supply of classroom furniture for district schools",
            "description": "Tables, chairs, benches, wooden furniture",
        },
        {
            "title": "AMC for hospital management software",
            "description": "Maintenance and support of existing software platform",
        },
        {
            "title": "Construction of boundary wall and civil works",
            "description": "Masonry, cement, and structural repair",
        },
    ]

    for idx, sample in enumerate(samples, start=1):
        result = score_bid_text(sample["title"], sample["description"])
        print(
            {
                "sample": idx,
                "title": sample["title"],
                "is_relevant": result.is_relevant,
                "score": result.score,
                "include_matches": result.include_matches,
                "exclude_matches": result.exclude_matches,
                "reason": result.reason,
            }
        )


if __name__ == "__main__":
    main()
