from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import PipelineRun


class PipelineRunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_run(self, status: str = "running") -> PipelineRun:
        run = PipelineRun(
            status=status,
            started_at=datetime.utcnow(),
        )
        self.db.add(run)
        self.db.flush()
        return run

    def mark_success(
        self,
        run: PipelineRun,
        bids_discovered: int = 0,
        bids_filtered: int = 0,
    ) -> PipelineRun:
        run.status = "success"
        run.ended_at = datetime.utcnow()
        run.bids_discovered = bids_discovered
        run.bids_filtered = bids_filtered
        self.db.flush()
        return run

    def mark_failed(self, run: PipelineRun, error_count: int = 1) -> PipelineRun:
        run.status = "failed"
        run.ended_at = datetime.utcnow()
        run.error_count = error_count
        self.db.flush()
        return run