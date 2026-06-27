from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import requests


@dataclass
class DownloadResult:
    url: str
    local_path: str
    file_size: int
    content_hash: str
    mime_type: str | None
    status_code: int


class FileDownloader:
    def __init__(self, session: requests.Session | None = None, timeout: int = 60) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout

    def download_to_path(self, url: str, destination: Path) -> DownloadResult:
        destination.parent.mkdir(parents=True, exist_ok=True)

        with self.session.get(url, stream=True, timeout=self.timeout) as response:
            response.raise_for_status()

            hasher = hashlib.sha256()
            total_size = 0

            with destination.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    f.write(chunk)
                    hasher.update(chunk)
                    total_size += len(chunk)

            return DownloadResult(
                url=url,
                local_path=str(destination),
                file_size=total_size,
                content_hash=hasher.hexdigest(),
                mime_type=response.headers.get("Content-Type"),
                status_code=response.status_code,
            )