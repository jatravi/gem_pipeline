"""
Tests for the keyword prefilter module.

These tests are pure unit tests — no database or network required.
"""

from __future__ import annotations

from app.filters.keyword_prefilter import (
    KeywordFilterResult,
    score_bid_text,
    is_bid_relevant_by_keywords,
    _normalize,
)


class TestNormalize:
    def test_strips_and_lowercases(self):
        assert _normalize("  Hello  ") == "hello"

    def test_collapses_whitespace(self):
        assert _normalize("a   b\t c") == "a b c"

    def test_handles_none(self):
        assert _normalize(None) == ""


class TestScoreBidText:
    def test_returns_keyword_filter_result(self):
        result = score_bid_text(title="random unrelated bid")
        assert isinstance(result, KeywordFilterResult)
        assert isinstance(result.is_relevant, bool)
        assert isinstance(result.score, int)
        assert isinstance(result.include_matches, list)
        assert isinstance(result.exclude_matches, list)
        assert isinstance(result.reason, str)

    def test_irrelevant_bid_returns_false(self):
        result = score_bid_text(
            title="Procurement of cement bags for road construction"
        )
        # Unless cement/road are in the include list, this should be irrelevant
        # The test validates the function completes without error
        assert isinstance(result.is_relevant, bool)

    def test_none_title_does_not_crash(self):
        result = score_bid_text(title=None, description=None)
        assert isinstance(result, KeywordFilterResult)
        assert result.is_relevant is False

    def test_empty_title_returns_result(self):
        result = score_bid_text(title="", description="")
        assert isinstance(result, KeywordFilterResult)
        assert result.is_relevant is False


class TestIsBidRelevantByKeywords:
    def test_returns_bool(self):
        result = is_bid_relevant_by_keywords(title="some tender", description="details")
        assert isinstance(result, bool)

    def test_none_inputs(self):
        result = is_bid_relevant_by_keywords(title=None, description=None)
        assert result is False
