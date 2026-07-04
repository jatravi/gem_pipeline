from __future__ import annotations

from decimal import Decimal
from pydantic import BaseModel, Field


class TenderLLMExtraction(BaseModel):
    tender_title: str | None = Field(default=None)
    issuing_organization: str | None = Field(default=None)
    scope_of_work: str | None = Field(default=None)
    eligibility_criteria: str | None = Field(default=None)
    earnest_money_deposit: str | None = Field(default=None)
    tender_fee: str | None = Field(default=None)
    bid_submission_deadline: str | None = Field(default=None)
    work_completion_timeline: str | None = Field(default=None)
    contact_details: str | None = Field(default=None)
    source_summary: str | None = Field(default=None)
    confidence_notes: str | None = Field(default=None)


class LLMUsageMetadata(BaseModel):
    model: str
    provider: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cost_inr: Decimal | None = None
    fallback_used: bool = False


class TenderLLMExtractionResult(BaseModel):
    extraction: TenderLLMExtraction
    usage: LLMUsageMetadata