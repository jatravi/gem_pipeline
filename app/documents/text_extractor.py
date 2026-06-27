from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pdfplumber


@dataclass
class TextExtractionResult:
    raw_text: str
    page_count: int
    method: str


class PdfTextExtractor:
    def extract(self, pdf_path: str | Path) -> TextExtractionResult:
        pdf_path = Path(pdf_path)
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