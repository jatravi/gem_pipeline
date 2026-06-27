from pathlib import Path

from app.documents.downloader import FileDownloader
from app.sources.gem.documents import build_bid_document_url


def main() -> None:
    source_bid_id = "9462710"  # replace if needed
    url = build_bid_document_url(source_bid_id)

    downloader = FileDownloader()
    result = downloader.download_to_path(
        url=url,
        destination=Path("data/raw/gem") / f"{source_bid_id}.pdf",
    )

    print(
        {
            "url": result.url,
            "local_path": result.local_path,
            "file_size": result.file_size,
            "content_hash": result.content_hash,
            "mime_type": result.mime_type,
            "status_code": result.status_code,
        }
    )


if __name__ == "__main__":
    main()