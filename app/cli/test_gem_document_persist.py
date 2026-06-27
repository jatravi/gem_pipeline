from pathlib import Path

from app.db.session import SessionLocal
from app.documents.downloader import FileDownloader
from app.repositories.bid_document_repository import BidDocumentRepository
from app.repositories.bid_repository import BidRepository
from app.sources.gem.documents import build_bid_document_url


def main() -> None:
    db = SessionLocal()
    try:
        bid_repo = BidRepository(db)
        doc_repo = BidDocumentRepository(db)

        bid = bid_repo.get_by_bid_number("GEM/2026/B/7659564")
        if not bid:
            raise RuntimeError("Bid not found")

        if not bid.source_bid_id:
            raise RuntimeError("Bid has no source_bid_id")

        source_bid_id = bid.source_bid_id
        url = build_bid_document_url(source_bid_id)

        destination = Path("data/raw/gem") / f"{source_bid_id}.pdf"
        downloader = FileDownloader()
        result = downloader.download_to_path(url=url, destination=destination)

        document = doc_repo.create_downloaded_document(
            bid_id=bid.id,
            file_name=f"{source_bid_id}.pdf",
            document_url=url,
            local_path=result.local_path,
            file_size=result.file_size,
            content_hash=result.content_hash,
            mime_type=result.mime_type,
            document_type="main_bid_document",
            sequence_no=1,
        )
        # updated = doc_repo.update_text_processing(
        #     document_id=document.id,
        #     raw_text="raw sample text",
        #     cleaned_text="cleaned sample text",
        #     text_hash="abc123",
        #     text_extraction_method="test",
        #     page_count=3,
        # )

        # db.commit()

        # print(
        #     {
        #         "document_id": updated.id,
        #         "processing_status": updated.processing_status,
        #         "text_hash": updated.text_hash,
        #         "page_count": updated.page_count,
        #     }
        # )


        # failed = doc_repo.mark_processing_failed(
        #     document_id=document.id,
        #     error_message="sample failure",
        # )
        # db.commit()

        # print(
        #     {
        #         "document_id": failed.id,
        #         "processing_status": failed.processing_status,
        #         "processing_error": failed.processing_error,
        #     }
        # )
        
        db.commit()

        print(
            {
                "bid_id": bid.id,
                "document_id": document.id,
                "file_name": document.file_name,
                "mime_type": document.mime_type,
                "file_size": document.file_size,
                "processing_status": document.processing_status,
            }
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()