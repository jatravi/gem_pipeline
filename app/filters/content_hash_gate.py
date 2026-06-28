from __future__ import annotations


def should_skip_llm_due_to_same_text(
    *,
    current_text_hash: str | None,
    previous_text_hash: str | None,
) -> bool:
    if not current_text_hash or not previous_text_hash:
        return False
    return current_text_hash == previous_text_hash