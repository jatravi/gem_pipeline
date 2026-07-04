"""
Tests for the text cleaning and hashing utilities.
"""
from __future__ import annotations

from app.documents.text_cleaner import clean_document_text
from app.documents.text_hashing import compute_text_hash


class TestCleanDocumentText:
    def test_normalizes_crlf(self):
        result = clean_document_text("hello\r\nworld")
        assert "\r" not in result
        assert "hello\nworld" == result

    def test_collapses_whitespace(self):
        result = clean_document_text("a   b\tc")
        assert result == "a b c"

    def test_collapses_blank_lines(self):
        result = clean_document_text("a\n\n\n\n\nb")
        assert result == "a\n\nb"

    def test_strips_leading_trailing(self):
        result = clean_document_text("  hello  ")
        assert result == "hello"

    def test_empty_string(self):
        result = clean_document_text("")
        assert result == ""


class TestComputeTextHash:
    def test_deterministic(self):
        h1 = compute_text_hash("hello world")
        h2 = compute_text_hash("hello world")
        assert h1 == h2

    def test_different_inputs_different_hashes(self):
        h1 = compute_text_hash("hello")
        h2 = compute_text_hash("world")
        assert h1 != h2

    def test_returns_hex_string(self):
        result = compute_text_hash("test")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest

    def test_empty_string(self):
        result = compute_text_hash("")
        assert isinstance(result, str)
        assert len(result) == 64
