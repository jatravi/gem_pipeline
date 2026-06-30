from app.pipelines.gem_discovery_pipeline import run_gem_discovery_pipeline


def main() -> None:
    run_gem_discovery_pipeline(limit=20)


if __name__ == "__main__":
    main()

# from app.llm.client import FakeLLMExtractor


# def main():
#     extractor = FakeLLMExtractor()

#     result = extractor.extract_tender_details(
#         """
#         Tender for Microsoft 365 Email Apps and Defender Licenses.
#         Issuing authority: Example Government Department.
#         Bid submission deadline: 15 July 2026.
#         Tender fee: Rs. 1,000.
#         """
#     )

#     print(result.model_dump())


# if __name__ == "__main__":
#     main()