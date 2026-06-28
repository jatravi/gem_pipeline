from __future__ import annotations

from pathlib import Path

from app.db.models import BidDocument
from app.db.session import SessionLocal
from app.documents.downloader import FileDownloader
from app.documents.text_cleaner import clean_document_text
from app.documents.text_extractor import PdfTextExtractor
from app.documents.text_hashing import compute_text_hash
from app.pipelines.gem_filter_pipeline import FilteredBidResult
from app.repositories.bid_document_repository import BidDocumentRepository
from app.repositories.bid_repository import BidRepository
from app.sources.gem.documents import build_bid_document_url


def run_document_download_pipeline(
    candidates: list[FilteredBidResult],
) -> list[BidDocument]:
    """
    Download documents for keyword-filtered bids.
    """

    db = SessionLocal()

    try:
        bid_repository = BidRepository(db)
        document_repository = BidDocumentRepository(db)
        downloader = FileDownloader()

        downloaded_documents: list[BidDocument] = []

        for candidate in candidates:

            bid = bid_repository.get_by_id(candidate.bid_id)

            if bid is None:
                continue

            if not bid.source_bid_id:
                continue

            try:
                document_url = build_bid_document_url(
                    bid.source_bid_id
                )

                destination = (
                    Path("data")
                    / "raw"
                    / "gem"
                    / f"{bid.source_bid_id}.pdf"
                )

                result = downloader.download_to_path(
                    url=document_url,
                    destination=destination,
                )

                document, created = (
                    document_repository.upsert_downloaded_document(
                        bid_id=bid.id,
                        file_name=destination.name,
                        document_url=result.url,
                        local_path=result.local_path,
                        file_size=result.file_size,
                        content_hash=result.content_hash,
                        mime_type=result.mime_type,
                    )
                )

                downloaded_documents.append(document)

                print(
                    {
                        "bid_id": bid.id,
                        "document_id": document.id,
                        "created": created,
                        "processing_status": document.processing_status,
                    }
                )

            except Exception as exc:
                print(
                    {
                        "bid_id": bid.id,
                        "download_failed": str(exc),
                    }
                )

        db.commit()

        return downloaded_documents

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def run_document_text_extraction_pipeline(
    documents: list[BidDocument],
) -> list[BidDocument]:
    """
    Extract text from downloaded documents.
    """

    db = SessionLocal()

    try:
        repository = BidDocumentRepository(db)
        extractor = PdfTextExtractor()

        processed_documents: list[BidDocument] = []

        for document in documents:

            document = db.merge(document)

            try:

                if not document.local_path:
                    raise RuntimeError(
                        f"Document {document.id} has no local_path."
                    )

                pdf_path = Path(document.local_path)

                if not pdf_path.exists():
                    raise FileNotFoundError(pdf_path)

                extraction = extractor.extract(pdf_path)

                cleaned_text = clean_document_text(
                    extraction.raw_text
                )

                text_hash = compute_text_hash(
                    cleaned_text
                )

                updated = repository.update_text_processing(
                    document_id=document.id,
                    raw_text=extraction.raw_text,
                    cleaned_text=cleaned_text,
                    text_hash=text_hash,
                    text_extraction_method=extraction.method,
                    page_count=extraction.page_count,
                )

                if updated is not None:
                    processed_documents.append(updated)

                print(
                    {
                        "document_id": document.id,
                        "status": "processed",
                        "pages": extraction.page_count,
                        "text_hash": text_hash,
                    }
                )

            except Exception as exc:

                repository.mark_processing_failed(
                    document_id=document.id,
                    error_message=str(exc),
                )

                print(
                    {
                        "document_id": document.id,
                        "status": "failed",
                        "error": str(exc),
                    }
                )

        db.commit()

        return processed_documents

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()