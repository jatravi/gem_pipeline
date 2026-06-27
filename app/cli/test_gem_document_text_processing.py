from pathlib import Path

from app.db.session import SessionLocal
from app.documents.text_cleaner import clean_document_text
from app.documents.text_extractor import PdfTextExtractor
from app.documents.text_hashing import compute_text_hash
from app.repositories.bid_document_repository import BidDocumentRepository


def main() -> None:
    db = SessionLocal()
    try:
        repo = BidDocumentRepository(db)
        extractor = PdfTextExtractor()

        document = repo.get_latest_downloaded_document()
        if not document:
            raise RuntimeError("No downloaded document found")

        if not document.local_path:
            raise RuntimeError("Document has no local_path")

        pdf_path = Path(document.local_path)
        if not pdf_path.exists():
            raise RuntimeError(f"PDF file not found at {pdf_path}")

        extraction = extractor.extract(pdf_path)
        cleaned_text = clean_document_text(extraction.raw_text)
        text_hash = compute_text_hash(cleaned_text)

        updated = repo.update_text_processing(
            document_id=document.id,
            raw_text=extraction.raw_text,
            cleaned_text=cleaned_text,
            text_hash=text_hash,
            text_extraction_method=extraction.method,
            page_count=extraction.page_count,
        )

        if not updated:
            raise RuntimeError("Failed to update document text processing")

        db.commit()

        print(
            {
                "document_id": updated.id,
                "page_count": updated.page_count,
                "raw_text_length": len(updated.raw_text or ""),
                "cleaned_text_length": len(updated.cleaned_text or ""),
                "text_hash": updated.text_hash,
                "processing_status": updated.processing_status,
                "text_extraction_method": updated.text_extraction_method,
            }
        )
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    main()