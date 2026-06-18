from datetime import datetime

from app.db.session import SessionLocal
from app.repositories.pipeline_run_repository import PipelineRunRepository
from app.schemas.bid import ParsedBid
from app.services.discovery_service import DiscoveryService


def main() -> None:
    db = SessionLocal()
    try:
        pipeline_repo = PipelineRunRepository(db)
        run = pipeline_repo.create_run(status="running")

        parsed_bid = ParsedBid(
            bid_number="GEM/2025/B/7056524",
            ra_number="GEM/2026/R/681104",
            title="AMC of Integrated Security and Surveillance System",
            ministry="Ministry of Labour and Employment",
            department=None,
            organisation=None,
            office=None,
            start_date=datetime(2026, 6, 13, 12, 0, 0),
            closing_date=datetime(2026, 6, 15, 1, 53, 0),
            status="ongoing",
            source_url="https://bidplus.gem.gov.in/all-bids",
        )

        service = DiscoveryService(db)
        bid, inserted = service.save_discovered_bid(parsed_bid, pipeline_run_id=run.id)

        pipeline_repo.mark_success(run, bids_discovered=1, bids_filtered=0)
        db.commit()

        print("Saved:", bid.bid_number)
        print("Inserted new:", inserted)
        print("Pipeline run:", run.id)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()