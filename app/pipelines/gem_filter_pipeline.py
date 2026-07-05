from __future__ import annotations

from dataclasses import asdict, dataclass

from app.db.session import SessionLocal
from app.filters.keyword_prefilter import (
    KeywordFilterResult,
    score_bid_text,
)
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


def run_keyword_prefilter_pipeline(
    limit: int = 20,
) -> list[FilteredBidResult]:
    """
    Apply keyword filtering to recently discovered bids.

    Returns only the bids that passed the keyword filter.
    """

    db = SessionLocal()

    try:
        bid_repository = BidRepository(db)

        bids = bid_repository.get_recent_bids(limit=limit)

        results: list[FilteredBidResult] = []

        for bid in bids:

            result: KeywordFilterResult = score_bid_text(
                title=bid.title,
                description=getattr(
                    bid,
                    "description",
                    None,
                ),
            )

            results.append(
                FilteredBidResult(
                    bid_id=bid.id,
                    bid_number=bid.bid_number or "",
                    title=bid.title,
                    is_relevant=result.is_relevant,
                    score=result.score,
                    include_matches=result.include_matches,
                    exclude_matches=result.exclude_matches,
                    reason=result.reason,
                )
            )

        candidates = [row for row in results if row.is_relevant]

        print(f"Scanned  : {len(results)} bids")
        print(f"Relevant : {len(candidates)} bids")

        if candidates:
            print("\nRelevant Bids")
            print("-" * 70)

            for row in candidates:
                print(asdict(row))

        return candidates

    finally:
        db.close()