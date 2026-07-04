"""
Tests for the content hash gate filter.
"""
from __future__ import annotations

from app.filters.content_hash_gate import should_skip_llm_due_to_same_text


class TestShouldSkipLLM:
    def test_same_hash_returns_true(self):
        h = "abc123"
        assert should_skip_llm_due_to_same_text(
            current_text_hash=h, previous_text_hash=h
        ) is True

    def test_different_hash_returns_false(self):
        assert should_skip_llm_due_to_same_text(
            current_text_hash="abc", previous_text_hash="xyz"
        ) is False

    def test_no_previous_hash_returns_false(self):
        assert should_skip_llm_due_to_same_text(
            current_text_hash="abc", previous_text_hash=None
        ) is False

    def test_no_current_hash_returns_false(self):
        assert should_skip_llm_due_to_same_text(
            current_text_hash=None, previous_text_hash="abc"
        ) is False

    def test_both_none_returns_false(self):
        assert should_skip_llm_due_to_same_text(
            current_text_hash=None, previous_text_hash=None
        ) is False
