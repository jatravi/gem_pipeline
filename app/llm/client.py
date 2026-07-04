from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Protocol

from langchain_ollama import ChatOllama

from app.config import settings
from app.llm.schemas import (
    LLMUsageMetadata,
    TenderLLMExtraction,
    TenderLLMExtractionResult,
)

PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "tender_extraction.txt"


class BaseLLMExtractor(Protocol):
    def extract_tender_details(self, text: str) -> TenderLLMExtractionResult:
        ...


def _load_system_prompt() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8").strip()
    return "Extract structured tender details. Return null for missing fields."


class FakeLLMExtractor:
    def extract_tender_details(self, text: str) -> TenderLLMExtractionResult:
        extraction = TenderLLMExtraction(
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
        usage = LLMUsageMetadata(
            model="fake",
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            cost_inr=Decimal("0"),
        )
        return TenderLLMExtractionResult(extraction=extraction, usage=usage)


class OllamaLLMExtractor:
    def __init__(self) -> None:
        self.system_prompt = _load_system_prompt()
        self.model = settings.OLLAMA_MODEL
        self.max_input_chars = settings.LLM_MAX_INPUT_CHARS

        self.llm = ChatOllama(
            model=self.model,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0,
        )
        self.structured_llm = self.llm.with_structured_output(TenderLLMExtraction)

    def extract_tender_details(self, text: str) -> TenderLLMExtractionResult:
        trimmed = (text or "").strip()[: self.max_input_chars]
        if not trimmed:
            raise ValueError("Cannot run LLM extraction on empty text.")

        extraction = self.structured_llm.invoke(
            [
                ("system", self.system_prompt),
                ("human", f"Extract structured tender data from:\n\n{trimmed}"),
            ]
        )

        # Ollama token usage often not reliably returned via LangChain metadata.
        usage = LLMUsageMetadata(
            model=self.model,
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            cost_inr=Decimal("0"),  # local model => API cost treated as 0
        )

        return TenderLLMExtractionResult(extraction=extraction, usage=usage)


class SafeLLMExtractor:
    def __init__(self, primary: BaseLLMExtractor, fallback: BaseLLMExtractor | None = None) -> None:
        self.primary = primary
        self.fallback = fallback

    def extract_tender_details(self, text: str) -> TenderLLMExtractionResult:
        try:
            return self.primary.extract_tender_details(text)
        except Exception as exc:
            if self.fallback is not None:
                print({"llm_primary_failed": str(exc), "fallback": "fake"})
                return self.fallback.extract_tender_details(text)
            raise


def get_llm_extractor() -> BaseLLMExtractor:
    provider = settings.LLM_PROVIDER.strip().lower()

    if provider == "fake":
        return FakeLLMExtractor()

    if provider == "ollama":
        primary = OllamaLLMExtractor()
        if settings.LLM_FALLBACK_TO_FAKE_ON_ERROR:
            return SafeLLMExtractor(primary=primary, fallback=FakeLLMExtractor())
        return primary

    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")