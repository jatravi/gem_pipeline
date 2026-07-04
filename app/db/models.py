from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_number: Mapped[str | None] = mapped_column(Text, unique=True, index=True)
    ra_number: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    ministry: Mapped[str | None] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(Text)
    organisation: Mapped[str | None] = mapped_column(Text)
    office: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[datetime | None] = mapped_column(DateTime)
    closing_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    estimated_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    emd_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    status: Mapped[str | None] = mapped_column(String(50))
    source_url: Mapped[str | None] = mapped_column(Text)
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    raw_listing_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_bid_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parent_source_bid_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    documents: Mapped[list["BidDocument"]] = relationship(back_populates="bid")
    events: Mapped[list["BidEvent"]] = relationship(back_populates="bid")
    extractions: Mapped[list["BidExtraction"]] = relationship(back_populates="bid")
    classifications: Mapped[list["BidClassification"]] = relationship(back_populates="bid")
    reviews: Mapped[list["BidReview"]] = relationship(back_populates="bid")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    bids_discovered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bids_filtered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pdfs_downloaded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    llm_calls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_cost_inr: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class BidEvent(Base):
    __tablename__ = "bid_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    pipeline_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    bid: Mapped["Bid"] = relationship(back_populates="events")


class BidDocument(Base):
    __tablename__ = "bid_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    document_type: Mapped[str | None] = mapped_column(String(100))
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    document_url: Mapped[str | None] = mapped_column(Text)
    local_path: Mapped[str | None] = mapped_column(Text)
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    content_hash: Mapped[str | None] = mapped_column(String(128))
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    sequence_no: Mapped[int | None] = mapped_column(Integer)
    raw_text: Mapped[str | None] = mapped_column(Text)
    cleaned_text: Mapped[str | None] = mapped_column(Text)
    text_hash: Mapped[str | None] = mapped_column(String(128))
    text_extracted_at: Mapped[datetime | None] = mapped_column(DateTime)
    text_extraction_method: Mapped[str | None] = mapped_column(String(50))
    page_count: Mapped[int | None] = mapped_column(Integer)
    processing_status: Mapped[str | None] = mapped_column(String(50))
    processing_error: Mapped[str | None] = mapped_column(Text)

    bid: Mapped["Bid"] = relationship(back_populates="documents")

class BidExtraction(Base):
    __tablename__ = "bid_extractions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    extraction_version: Mapped[str | None] = mapped_column(String(50))
    is_current: Mapped[bool] = mapped_column(nullable=False, default=True)
    title: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[str | None] = mapped_column(Text)
    value_inr: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    emd_inr: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    min_turnover_inr: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    experience_years: Mapped[int | None] = mapped_column(Integer)
    published_date: Mapped[datetime | None] = mapped_column(DateTime)
    prebid_date: Mapped[datetime | None] = mapped_column(DateTime)
    close_date: Mapped[datetime | None] = mapped_column(DateTime)
    ministry: Mapped[str | None] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(Text)
    organisation: Mapped[str | None] = mapped_column(Text)
    office: Mapped[str | None] = mapped_column(Text)
    relevant: Mapped[bool | None] = mapped_column()
    relevance_reason: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    prompt_version: Mapped[str | None] = mapped_column(String(50))
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    raw_response_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    bid: Mapped["Bid"] = relationship(back_populates="extractions")


class BidClassification(Base):
    __tablename__ = "bid_classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    classification_version: Mapped[str | None] = mapped_column(String(50))
    is_current: Mapped[bool | None] = mapped_column(default=True)
    classification_label: Mapped[str | None] = mapped_column(String(50))
    relevance_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    eligibility_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    decision_reason: Mapped[str | None] = mapped_column(Text)
    company_profile_version: Mapped[str | None] = mapped_column(String(50))
    model_version: Mapped[str | None] = mapped_column(String(50))
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    bid: Mapped["Bid"] = relationship(back_populates="classifications")


class BidReview(Base):
    __tablename__ = "bid_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"), nullable=False)
    extraction_id: Mapped[int | None] = mapped_column(ForeignKey("bid_extractions.id"))
    classification_id: Mapped[int | None] = mapped_column(ForeignKey("bid_classifications.id"))
    review_decision: Mapped[str] = mapped_column(String(50), nullable=False)
    review_reason: Mapped[str | None] = mapped_column(Text)
    reviewer_name: Mapped[str | None] = mapped_column(String(100))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    bid: Mapped["Bid"] = relationship(back_populates="reviews")

class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_version: Mapped[str] = mapped_column(String(50), unique=True, nullable=False,)
    company_name: Mapped[str] = mapped_column(Text,nullable=False,)
    services: Mapped[list[str]] = mapped_column(JSONB,nullable=False,default=list,)
    industries: Mapped[list[str]] = mapped_column(JSONB,nullable=False,default=list,)
    min_project_value_inr: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    max_project_value_inr: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    min_turnover_inr: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    certifications: Mapped[list[str]] = mapped_column(JSONB,nullable=False,default=list,)
    excluded_keywords: Mapped[list[str]] = mapped_column(JSONB,nullable=False,default=list,)
    preferred_keywords: Mapped[list[str]] = mapped_column(JSONB,nullable=False,default=list,)
    geo_preferences: Mapped[list[str]] = mapped_column(JSONB,nullable=False,default=list,)
    active: Mapped[bool] = mapped_column( Boolean,nullable=False,default=True,)
    created_at: Mapped[datetime] = mapped_column(DateTime,nullable=False,server_default=func.now(),)
    updated_at: Mapped[datetime] = mapped_column(DateTime,nullable=False,server_default=func.now(),onupdate=func.now(),)