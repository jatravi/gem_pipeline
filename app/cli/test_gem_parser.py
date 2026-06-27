from app.sources.gem.client import GeMClient
from app.sources.gem.parser import GeMListingParser


def main() -> None:
    client = GeMClient()
    parser = GeMListingParser()

    payload = client.fetch_listing_data()
    bids = parser.parse_listing_docs(payload)

    print(f"Found {len(bids)} bids")
    for bid in bids[:5]:
        print("-" * 80)
        print(bid)


if __name__ == "__main__":
    main()