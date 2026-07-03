from __future__ import annotations

from pathlib import Path
from typing import Protocol

from openai import OpenAI

from app.config import settings
from app.llm.schemas import TenderLLMExtraction


PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "tender_extraction.txt"


class BaseLLMExtractor(Protocol):
    def extract_tender_details(self, text: str) -> TenderLLMExtraction:
        ...


def _load_system_prompt() -> str:
    if not PROMPT_FILE.exists():
        return (
            "You are an information extraction assistant for government tender documents. "
            "Extract only explicitly stated information and return structured output."
        )
    return PROMPT_FILE.read_text(encoding="utf-8").strip()


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


class OpenAILLMExtractor:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        max_input_chars: int = 15000,
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = _load_system_prompt()
        self.max_input_chars = max_input_chars

    def extract_tender_details(self, text: str) -> TenderLLMExtraction:
        trimmed_text = (text or "").strip()[: self.max_input_chars]

        if not trimmed_text:
            raise ValueError("Cannot run LLM extraction on empty text.")

        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Extract structured tender information from the following text. "
                        "Return null for missing fields.\n\n"
                        f"TENDER TEXT:\n{trimmed_text}"
                    ),
                },
            ],
            text_format=TenderLLMExtraction,
        )

        if response.output_parsed is None:
            raise ValueError("LLM response did not return parsed structured output.")

        return response.output_parsed


def get_llm_extractor() -> BaseLLMExtractor:
    provider = settings.LLM_PROVIDER.strip().lower()

    if provider == "fake":
        return FakeLLMExtractor()

    if provider == "openai":
        if not settings.LLM_API_KEY:
            raise ValueError("LLM_PROVIDER=openai but LLM_API_KEY is missing.")
        return OpenAILLMExtractor(
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            max_input_chars=settings.LLM_MAX_INPUT_CHARS,
        )

    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")