from app.filters.content_hash_gate import should_skip_llm_due_to_same_text


def main() -> None:
    samples = [
        {
            "name": "same hashes",
            "current_text_hash": "abc123",
            "previous_text_hash": "abc123",
        },
        {
            "name": "different hashes",
            "current_text_hash": "abc123",
            "previous_text_hash": "xyz789",
        },
        {
            "name": "missing current hash",
            "current_text_hash": None,
            "previous_text_hash": "xyz789",
        },
        {
            "name": "missing previous hash",
            "current_text_hash": "abc123",
            "previous_text_hash": None,
        },
    ]

    for sample in samples:
        result = should_skip_llm_due_to_same_text(
            current_text_hash=sample["current_text_hash"],
            previous_text_hash=sample["previous_text_hash"],
        )
        print(
            {
                "name": sample["name"],
                "current_text_hash": sample["current_text_hash"],
                "previous_text_hash": sample["previous_text_hash"],
                "should_skip": result,
            }
        )


if __name__ == "__main__":
    main()