from __future__ import annotations

from dataclasses import asdict, dataclass

from app.db.session import SessionLocal
from app.filters.keyword_prefilter import KeywordFilterResult, score_bid_text
from app.repositories.bid_repository import BidRepository


@dataclass
class FilteredBidResult:
    bid_id: int
    bid_number: str
    title: str | None
    is_relevant: bool
    score: int
    include_matches: list[str]
    exclude_matches: list[str]
    reason: str


def run_keyword_prefilter_pipeline(limit: int = 20) -> list[FilteredBidResult]:
    db = SessionLocal()
    try:
        bid_repo = BidRepository(db)

        # Replace with a better repository method later if needed.
        bids = bid_repo.get_recent_bids(limit=limit)

        results: list[FilteredBidResult] = []

        for bid in bids:
            result: KeywordFilterResult = score_bid_text(
                title=getattr(bid, "title", None),
                description=getattr(bid, "description", None),
            )

            filtered = FilteredBidResult(
                bid_id=bid.id,
                bid_number=bid.bid_number,
                title=getattr(bid, "title", None),
                is_relevant=result.is_relevant,
                score=result.score,
                include_matches=result.include_matches,
                exclude_matches=result.exclude_matches,
                reason=result.reason,
            )
            results.append(filtered)

        for row in results:
            print(asdict(row))

        return results
    finally:
        db.close()