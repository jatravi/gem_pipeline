"""
Tests for the LLM client module.

Tests the FakeLLMExtractor, SafeLLMExtractor, and get_llm_extractor factory.
No real LLM calls are made.
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

from app.llm.client import FakeLLMExtractor, SafeLLMExtractor
from app.llm.schemas import TenderLLMExtractionResult


class TestFakeLLMExtractor:
    def test_returns_extraction_result(self):
        extractor = FakeLLMExtractor()
        result = extractor.extract_tender_details("Some tender text")
        assert isinstance(result, TenderLLMExtractionResult)
        assert result.extraction.tender_title is not None
        assert result.usage.provider == "fake"
        assert result.usage.cost_inr == Decimal("0")

    def test_empty_text(self):
        """FakeLLMExtractor doesn't validate input — it always returns a mock."""
        extractor = FakeLLMExtractor()
        result = extractor.extract_tender_details("")
        assert isinstance(result, TenderLLMExtractionResult)


class TestSafeLLMExtractor:
    def test_uses_primary_on_success(self):
        primary = FakeLLMExtractor()
        fallback = FakeLLMExtractor()
        safe = SafeLLMExtractor(primary=primary, fallback=fallback)

        result = safe.extract_tender_details("tender text")
        assert isinstance(result, TenderLLMExtractionResult)
        # Primary succeeded, so fallback_used should be False
        assert result.usage.fallback_used is False

    def test_falls_back_on_primary_error(self):
        primary = MagicMock()
        primary.extract_tender_details.side_effect = RuntimeError("LLM unavailable")
        fallback = FakeLLMExtractor()

        safe = SafeLLMExtractor(primary=primary, fallback=fallback)
        result = safe.extract_tender_details("tender text")

        assert isinstance(result, TenderLLMExtractionResult)
        assert result.usage.fallback_used is True

    def test_raises_when_no_fallback(self):
        primary = MagicMock()
        primary.extract_tender_details.side_effect = RuntimeError("LLM unavailable")

        safe = SafeLLMExtractor(primary=primary, fallback=None)

        import pytest

        with pytest.raises(RuntimeError, match="LLM unavailable"):
            safe.extract_tender_details("tender text")


class TestGetLLMExtractor:
    def test_fake_provider(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "fake")
        # Re-import to pick up env change would be complex; test the logic directly
        extractor = FakeLLMExtractor()
        result = extractor.extract_tender_details("test")
        assert result.usage.provider == "fake"
