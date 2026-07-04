from __future__ import annotations

from sqlalchemy.orm import Session
from app.db.models import CompanyProfile

class CompanyProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_profile(self) -> CompanyProfile | None:
        """
        Retrieves the first active company profile.
        """
        return (
            self.db.query(CompanyProfile)
            .filter(CompanyProfile.active.is_(True))
            .first()
        )
