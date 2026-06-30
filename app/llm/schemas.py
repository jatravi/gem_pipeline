from __future__ import annotations

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