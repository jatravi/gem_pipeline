from __future__ import annotations
import json
import time
from decimal import Decimal
from pathlib import Path
from typing import Protocol
import requests

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy import text

from app.config import settings
from app.llm.schemas import (
    LLMUsageMetadata,
    TenderLLMExtraction,
    TenderLLMExtractionResult,
)

PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "tender_extraction.txt"


class BaseLLMExtractor(Protocol):
    def extract_tender_details(self, text: str) -> TenderLLMExtractionResult: ...


def _load_system_prompt() -> str:
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8").strip()
    return "Extract structured tender details. Return null for missing fields."


def check_llm_health() -> None:
    """
    Validate the configured LLM provider before pipeline execution.
    """

    provider = settings.LLM_PROVIDER.strip().lower()

    if provider == "fake":
        return

    if provider == "ollama":
        base_url = settings.OLLAMA_BASE_URL.rstrip("/")

        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()

        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"Unable to connect to Ollama at {base_url}.\n"
                "Make sure the Ollama server is running."
            ) from exc

        models = [m["name"] for m in data.get("models", [])]
        configured_model = settings.OLLAMA_MODEL

        found = any(
            m == configured_model
            or m.split(":")[0] == configured_model.split(":")[0]
            for m in models
        )

        if not found:
            raise RuntimeError(
                f"Ollama model '{configured_model}' is not installed.\n"
                f"Installed models: {models}\n"
                f"Run:\n\nollama pull {configured_model}"
            )

        return

    if provider == "openai":
        if not settings.LLM_API_KEY:
            raise RuntimeError("LLM_API_KEY is missing.")

        try:
            ChatOpenAI(
                model=settings.LLM_MODEL,
                api_key=settings.LLM_API_KEY,
                temperature=0,
            ).invoke("ping")
        except Exception as exc:
            raise RuntimeError(
                f"Unable to connect to OpenAI using model '{settings.LLM_MODEL}'."
            ) from exc

        return

    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is missing.")

        try:
            ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0,
            ).invoke("ping")
        except Exception as exc:
            raise RuntimeError(
                f"Unable to connect to Gemini using model '{settings.GEMINI_MODEL}'."
            ) from exc

        return

    raise ValueError(f"Unsupported LLM provider: {provider}")


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
            provider="fake",
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            cost_inr=Decimal("0"),
        )
        return TenderLLMExtractionResult(extraction=extraction, usage=usage)


class OllamaLLMExtractor:
    def __init__(self) -> None:
        check_llm_health()

        self.system_prompt = _load_system_prompt()
        self.model = settings.OLLAMA_MODEL
        self.max_input_chars = settings.LLM_MAX_INPUT_CHARS

        self.llm = ChatOllama(
            model=self.model,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0,
            request_timeout=300,
        )

    def extract_tender_details(self, text: str) -> TenderLLMExtractionResult:
        trimmed = (text or "").strip()[: self.max_input_chars]

        if not trimmed:
            raise ValueError("Cannot run LLM extraction on empty text.")

        print("=" * 80)
        print("OLLAMA DEBUG")
        print(f"Model: {self.model}")
        print(f"Characters: {len(trimmed)}")
        print(f"Approx Tokens: {len(trimmed)//4}")
        print("=" * 80)

        messages = [
            ("system", self.system_prompt),
            ("human", f"Extract structured tender data from:\n\n{trimmed}"),
        ]

        start = time.perf_counter()

        response = self.llm.invoke(messages)

        elapsed = time.perf_counter() - start

        print("=" * 80)
        print(f"LLM finished in {elapsed:.2f} seconds")
        print("=" * 80)

        print("RAW RESPONSE:")
        print(response.content)
        print("=" * 80)

        try:
            data = json.loads(response.content)
        except Exception as e:
            raise RuntimeError(
                f"Model did not return valid JSON.\n\n{response.content}"
            ) from e

        extraction = TenderLLMExtraction.model_validate(data)

        usage = LLMUsageMetadata(
            model=self.model,
            provider="ollama",
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            cost_inr=Decimal("0"),
        )

        return TenderLLMExtractionResult(
            extraction=extraction,
            usage=usage,
        )


class OpenAILLMExtractor:
    def __init__(self) -> None:
        self.system_prompt = _load_system_prompt()
        self.model = settings.LLM_MODEL
        self.max_input_chars = settings.LLM_MAX_INPUT_CHARS
        self.api_key = settings.LLM_API_KEY

        self.llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=0,
        )
        # include_raw=True allows us to capture the token usage metadata from the AIMessage response
        self.structured_llm = self.llm.with_structured_output(
            TenderLLMExtraction, include_raw=True
        )

    def extract_tender_details(self, text: str) -> TenderLLMExtractionResult:
        trimmed = (text or "").strip()[: self.max_input_chars]
        if not trimmed:
            raise ValueError("Cannot run LLM extraction on empty text.")

        res = self.structured_llm.invoke(
            [
                ("system", self.system_prompt),
                ("human", f"Extract structured tender data from:\n\n{trimmed}"),
            ]
        )

        extraction = res.get("parsed")
        raw_msg = res.get("raw")

        input_tokens = None
        output_tokens = None
        total_tokens = None

        if raw_msg and hasattr(raw_msg, "response_metadata"):
            token_usage = raw_msg.response_metadata.get("token_usage", {})
            if token_usage:
                input_tokens = token_usage.get("prompt_tokens")
                output_tokens = token_usage.get("completion_tokens")
                total_tokens = token_usage.get("total_tokens")

        # Cost calculations
        input_cost = Decimal("0")
        output_cost = Decimal("0")
        if input_tokens is not None:
            input_cost = (
                Decimal(input_tokens) / Decimal("1000")
            ) * settings.LLM_INPUT_COST_PER_1K_TOKENS_INR
        if output_tokens is not None:
            output_cost = (
                Decimal(output_tokens) / Decimal("1000")
            ) * settings.LLM_OUTPUT_COST_PER_1K_TOKENS_INR
        cost_inr = input_cost + output_cost

        usage = LLMUsageMetadata(
            model=self.model,
            provider="openai",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_inr=cost_inr,
        )

        return TenderLLMExtractionResult(extraction=extraction, usage=usage)


class SafeLLMExtractor:
    def __init__(
        self, primary: BaseLLMExtractor, fallback: BaseLLMExtractor | None = None
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    def extract_tender_details(self, text: str) -> TenderLLMExtractionResult:
        try:
            return self.primary.extract_tender_details(text)
        except Exception as exc:
            if self.fallback is not None:
                # Log structured fallback event without exposing sensitive info
                print(
                    {
                        "event": "llm_fallback_triggered",
                        "primary_error": str(exc),
                        "fallback_provider": "fake",
                    }
                )
                result = self.fallback.extract_tender_details(text)
                result.usage.fallback_used = True
                return result
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

    if provider == "openai":
        primary = OpenAILLMExtractor()
        if settings.LLM_FALLBACK_TO_FAKE_ON_ERROR:
            return SafeLLMExtractor(primary=primary, fallback=FakeLLMExtractor())
        return primary

    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")

class GeminiLLMExtractor:
    def __init__(self) -> None:
        self.system_prompt = _load_system_prompt()
        self.model = settings.GEMINI_MODEL
        self.max_input_chars = settings.LLM_MAX_INPUT_CHARS

        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0,
        )

        self.structured_llm = self.llm.with_structured_output(
            TenderLLMExtraction,
            include_raw=True,
        )

    def extract_tender_details(
        self,
        text: str,
    ) -> TenderLLMExtractionResult:

        trimmed = (text or "").strip()[: self.max_input_chars]

        if not trimmed:
            raise ValueError("Cannot run LLM extraction on empty text.")

        result = self.structured_llm.invoke(
            [
                ("system", self.system_prompt),
                ("human", f"Extract structured tender data from:\n\n{trimmed}"),
            ]
        )

        extraction = result.get("parsed")
        raw_msg = result.get("raw")

        input_tokens = None
        output_tokens = None
        total_tokens = None

        if raw_msg and hasattr(raw_msg, "usage_metadata"):
            usage = raw_msg.usage_metadata or {}

            input_tokens = usage.get("input_tokens")
            output_tokens = usage.get("output_tokens")
            total_tokens = usage.get("total_tokens")

        elif raw_msg and hasattr(raw_msg, "response_metadata"):
            usage = raw_msg.response_metadata.get("usage_metadata", {})

            input_tokens = usage.get("input_tokens")
            output_tokens = usage.get("output_tokens")
            total_tokens = usage.get("total_tokens")

        input_cost = Decimal("0")
        output_cost = Decimal("0")

        if input_tokens:
            input_cost = (
                Decimal(input_tokens) / Decimal("1000")
            ) * settings.LLM_INPUT_COST_PER_1K_TOKENS_INR

        if output_tokens:
            output_cost = (
                Decimal(output_tokens) / Decimal("1000")
            ) * settings.LLM_OUTPUT_COST_PER_1K_TOKENS_INR

        usage = LLMUsageMetadata(
            model=self.model,
            provider="gemini",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_inr=input_cost + output_cost,
        )

        return TenderLLMExtractionResult(
            extraction=extraction,
            usage=usage,
        )