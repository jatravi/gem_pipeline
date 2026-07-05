from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pdfplumber


class InvalidPDFError(Exception):
    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(f"Invalid PDF: {reason_code}")


@dataclass
class TextExtractionResult:
    raw_text: str
    page_count: int
    method: str


class PdfTextExtractor:
    def extract(self, pdf_path: str | Path) -> TextExtractionResult:
        pdf_path = Path(pdf_path)

        # 1. Validate file exists
        if not pdf_path.exists():
            raise InvalidPDFError("missing_file")

        # 2. Validate non-zero size
        if pdf_path.stat().st_size == 0:
            raise InvalidPDFError("empty_file")

        # 3. Validate first bytes start with %PDF-
        try:
            with open(pdf_path, "rb") as f:
                header = f.read(5)
                if header != b"%PDF-":
                    raise InvalidPDFError("invalid_pdf_signature")
        except OSError:
            # Handle standard OS errors reading file as missing_file
            raise InvalidPDFError("missing_file")

        # Extract text using pdfplumber
        try:
            page_texts: list[str] = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    page_texts.append(text)

                return TextExtractionResult(
                    raw_text="\n\n".join(page_texts),
                    page_count=len(pdf.pages),
                    method="pdfplumber",
                )
        except Exception as exc:
            # Keep standard unhandled parser errors caught under a generic invalid signature/format error
            # to make sure we don't throw unhandled exceptions
            raise InvalidPDFError("invalid_pdf_signature") from exc
