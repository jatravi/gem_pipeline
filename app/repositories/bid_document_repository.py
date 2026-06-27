from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import BidDocument


class BidDocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, document_id: int) -> BidDocument | None:
        return self.db.query(BidDocument).filter(BidDocument.id == document_id).first()

    def create_downloaded_document(
        self,
        *,
        bid_id: int,
        file_name: str,
        document_url: str,
        local_path: str | Path,
        file_size: int,
        content_hash: str,
        mime_type: str | None,
        document_type: str = "main_bid_document",
        sequence_no: int = 1,
        downloaded_at: datetime | None = None,
        processing_status: str = "downloaded",
    ) -> BidDocument:
        document = BidDocument(
            bid_id=bid_id,
            document_type=document_type,
            file_name=file_name,
            document_url=document_url,
            local_path=str(local_path),
            file_size=file_size,
            content_hash=content_hash,
            downloaded_at=downloaded_at or datetime.utcnow(),
            created_at=datetime.utcnow(),
            mime_type=mime_type,
            sequence_no=sequence_no,
            processing_status=processing_status,
        )
        self.db.add(document)
        self.db.flush()
        return document

    def update_text_processing(
        self,
        *,
        document_id: int,
        raw_text: str,
        cleaned_text: str,
        text_hash: str,
        text_extraction_method: str,
        page_count: int | None,
        text_extracted_at: datetime | None = None,
        processing_status: str = "processed",
    ) -> BidDocument | None:
        document = self.get_by_id(document_id)
        if not document:
            return None

        document.raw_text = raw_text
        document.cleaned_text = cleaned_text
        document.text_hash = text_hash
        document.text_extraction_method = text_extraction_method
        document.page_count = page_count
        document.text_extracted_at = text_extracted_at or datetime.utcnow()
        document.processing_status = processing_status
        document.processing_error = None
        self.db.flush()
        return document

    def mark_processing_failed(
        self,
        *,
        document_id: int,
        error_message: str,
    ) -> BidDocument | None:
        document = self.get_by_id(document_id)
        if not document:
            return None

        document.processing_status = "failed"
        document.processing_error = error_message
        self.db.flush()
        return document