from datetime import datetime
from decimal import Decimal
from typing import Optional, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    TIMESTAMP,
    VARCHAR,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_number: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    ra_number: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[Optional[str]] = mapped_column(Text)
    ministry: Mapped[Optional[str]] = mapped_column(Text)
    department: Mapped[Optional[str]] = mapped_column(Text)
    organisation: Mapped[Optional[str]] = mapped_column(Text)
    office: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=False))
    closing_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=False))
    estimated_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    emd_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    status: Mapped[Optional[str]] = mapped_column(VARCHAR(50))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    first_seen_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=False))
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=False))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )

    events: Mapped[list["BidEvent"]] = relationship(back_populates="bid")
    extractions: Mapped[list["BidExtraction"]] = relationship(back_populates="bid")
    documents: Mapped[list["BidDocument"]] = relationship(back_populates="bid")
    classifications: Mapped[list["BidClassification"]] = relationship(back_populates="bid")
    reviews: Mapped[list["BidReview"]] = relationship(back_populates="bid")


class BidEvent(Base):
    __tablename__ = "bid_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    event_details: Mapped[Optional[Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    pipeline_run_id: Mapped[Optional[int]] = mapped_column(Integer)

    bid: Mapped["Bid"] = relationship(back_populates="events")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=False))
    status: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    bids_discovered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bids_filtered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pdfs_downloaded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    llm_calls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_cost_inr: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class BidDocument(Base):
    __tablename__ = "bid_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    document_type: Mapped[Optional[str]] = mapped_column(VARCHAR(100))
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    document_url: Mapped[Optional[str]] = mapped_column(Text)
    local_path: Mapped[Optional[str]] = mapped_column(Text)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    content_hash: Mapped[Optional[str]] = mapped_column(VARCHAR(128))
    downloaded_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=False))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )

    bid: Mapped["Bid"] = relationship(back_populates="documents")


class BidExtraction(Base):
    __tablename__ = "bid_extractions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    extraction_version: Mapped[Optional[str]] = mapped_column(VARCHAR(50))
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    scope: Mapped[Optional[str]] = mapped_column(Text)
    value_inr: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    emd_inr: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    min_turnover_inr: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    experience_years: Mapped[Optional[int]] = mapped_column(Integer)
    published_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=False))
    prebid_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=False))
    close_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=False))
    ministry: Mapped[Optional[str]] = mapped_column(Text)
    department: Mapped[Optional[str]] = mapped_column(Text)
    organisation: Mapped[Optional[str]] = mapped_column(Text)
    office: Mapped[Optional[str]] = mapped_column(Text)
    relevant: Mapped[Optional[bool]] = mapped_column(Boolean)
    relevance_reason: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    prompt_version: Mapped[Optional[str]] = mapped_column(VARCHAR(50))
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    cost_inr: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    raw_response_json: Mapped[Optional[Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        server_default=func.now(),
    )

    bid: Mapped["Bid"] = relationship(back_populates="extractions")


class BidClassification(Base):
    __tablename__ = "bid_classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    classification_version: Mapped[Optional[str]] = mapped_column(VARCHAR(50))
    is_current: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    classification_label: Mapped[Optional[str]] = mapped_column(VARCHAR(50))
    relevance_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    eligibility_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    decision_reason: Mapped[Optional[str]] = mapped_column(Text)
    company_profile_version: Mapped[Optional[str]] = mapped_column(VARCHAR(50))
    model_version: Mapped[Optional[str]] = mapped_column(VARCHAR(50))
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    cost_inr: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    created_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
    )

    bid: Mapped["Bid"] = relationship(back_populates="classifications")


class BidReview(Base):
    __tablename__ = "bid_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    extraction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bid_extractions.id"))
    classification_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bid_classifications.id"))
    review_decision: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    review_reason: Mapped[Optional[str]] = mapped_column(Text)
    reviewer_name: Mapped[Optional[str]] = mapped_column(VARCHAR(100))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
    )

    bid: Mapped["Bid"] = relationship(back_populates="reviews")