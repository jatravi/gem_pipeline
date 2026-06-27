BASE_URL = "https://bidplus.gem.gov.in"
LISTING_PAGE_URL = f"{BASE_URL}/all-bids"
LISTING_DATA_URL = f"{BASE_URL}/all-bids-data"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": BASE_URL,
    "Referer": LISTING_PAGE_URL,
}