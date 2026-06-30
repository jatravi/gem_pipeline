from __future__ import annotations

from app.llm.schemas import TenderLLMExtraction


class FakeLLMExtractor:
    def extract_tender_details(self, text: str) -> TenderLLMExtraction:
        return TenderLLMExtraction(
            tender_title="Mock Tender Title",
            issuing_organization=None,
            scope_of_work="Mock extraction result for pipeline integration testing.",
            eligibility_criteria=None,
            earnest_money_deposit=None,
            tender_fee=None,
            bid_submission_deadline=None,
            work_completion_timeline=None,
            contact_details=None,
            source_summary="Mock summary generated without external LLM call.",
            confidence_notes="Fake extractor used for local integration testing.",
        )