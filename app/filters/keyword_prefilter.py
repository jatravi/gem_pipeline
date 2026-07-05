from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INCLUDE_KEYWORDS = {
    line.strip().lower()
    for line in (BASE_DIR / "configs" / "keyword_include.txt")
    .read_text(encoding="utf-8")
    .splitlines()
    if line.strip()
}

EXCLUDE_KEYWORDS = {
    line.strip().lower()
    for line in (BASE_DIR / "configs" / "keyword_exclude.txt")
    .read_text(encoding="utf-8")
    .splitlines()
    if line.strip()
}


@dataclass
class KeywordFilterResult:
    is_relevant: bool
    include_matches: list[str]
    exclude_matches: list[str]
    score: int
    reason: str


def _normalize(text: str | None) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _keyword_pattern(keyword: str) -> re.Pattern[str]:
    escaped = re.escape(keyword)
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


INCLUDE_PATTERNS = {kw: _keyword_pattern(kw) for kw in INCLUDE_KEYWORDS}

EXCLUDE_PATTERNS = {kw: _keyword_pattern(kw) for kw in EXCLUDE_KEYWORDS}


def _find_matches(
    text: str,
    patterns: dict[str, re.Pattern[str]],
) -> list[str]:
    return sorted(kw for kw, pattern in patterns.items() if pattern.search(text))


def score_bid_text(
    title: str | None, description: str | None = None
) -> KeywordFilterResult:
    combined = f"{_normalize(title)}\n{_normalize(description)}"

    include_matches = _find_matches(combined, INCLUDE_PATTERNS)
    exclude_matches = _find_matches(combined, EXCLUDE_PATTERNS)

    score = len(include_matches) - (2 * len(exclude_matches))

    if exclude_matches and not include_matches:
        return KeywordFilterResult(
            is_relevant=False,
            include_matches=include_matches,
            exclude_matches=exclude_matches,
            score=score,
            reason="Matched exclude keywords without any include keywords",
        )

    if score > 0:
        return KeywordFilterResult(
            is_relevant=True,
            include_matches=include_matches,
            exclude_matches=exclude_matches,
            score=score,
            reason="Positive keyword relevance score",
        )

    return KeywordFilterResult(
        is_relevant=False,
        include_matches=include_matches,
        exclude_matches=exclude_matches,
        score=score,
        reason="Insufficient include keyword evidence",
    )


def is_bid_relevant_by_keywords(
    title: str | None, description: str | None = None
) -> bool:
    return score_bid_text(title=title, description=description).is_relevant
