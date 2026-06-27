from sqlalchemy.orm import Session

from app.repositories.pipeline_run_repository import PipelineRunRepository
from app.services.discovery_service import DiscoveryService
from app.sources.gem.client import GeMClient
from app.sources.gem.normalizer import GeMBidNormalizer
from app.sources.gem.parser import GeMListingParser


class GeMDiscoveryRunner:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.client = GeMClient()
        self.parser = GeMListingParser()
        self.normalizer = GeMBidNormalizer()
        self.discovery_service = DiscoveryService(db)
        self.pipeline_run_repo = PipelineRunRepository(db)

    def run(self) -> dict:
        run = self.pipeline_run_repo.create_run(status="running")

        discovered_count = 0
        filtered_count = 0

        try:
            payload = self.client.fetch_listing_data()
            raw_bids = self.parser.parse_listing_docs(payload)

            for raw_bid in raw_bids:
                parsed_bid = self.normalizer.normalize(raw_bid)

                if not parsed_bid:
                    filtered_count += 1
                    continue

                self.discovery_service.save_discovered_bid(
                    parsed_bid=parsed_bid,
                    pipeline_run_id=run.id,
                )
                discovered_count += 1

            self.pipeline_run_repo.mark_success(
                run,
                bids_discovered=discovered_count,
                bids_filtered=filtered_count,
            )
            self.db.commit()

            return {
                "pipeline_run_id": run.id,
                "bids_discovered": discovered_count,
                "bids_filtered": filtered_count,
            }

        except Exception:
            self.db.rollback()
            self.pipeline_run_repo.mark_failed(run, error_count=1)
            self.db.commit()
            raise