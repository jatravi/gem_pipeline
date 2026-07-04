"""
Tests for the text extraction module (PdfTextExtractor and InvalidPDFError).

Uses temporary files — no external services needed.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from app.documents.text_extractor import InvalidPDFError, PdfTextExtractor


class TestInvalidPDFError:
    def test_has_reason_code(self):
        exc = InvalidPDFError("empty_file")
        assert exc.reason_code == "empty_file"
        assert "empty_file" in str(exc)

    def test_different_codes(self):
        for code in ("missing_file", "empty_file", "invalid_pdf_signature"):
            exc = InvalidPDFError(code)
            assert exc.reason_code == code


class TestPdfTextExtractor:
    def setup_method(self):
        self.extractor = PdfTextExtractor()

    def test_missing_file_raises(self):
        with pytest.raises(InvalidPDFError, match="missing_file"):
            self.extractor.extract(Path("/nonexistent/path/file.pdf"))

    def test_empty_file_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"")
            tmp_path = f.name

        try:
            with pytest.raises(InvalidPDFError, match="empty_file"):
                self.extractor.extract(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_invalid_signature_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"<html>This is not a PDF</html>")
            tmp_path = f.name

        try:
            with pytest.raises(InvalidPDFError, match="invalid_pdf_signature"):
                self.extractor.extract(tmp_path)
        finally:
            os.unlink(tmp_path)
