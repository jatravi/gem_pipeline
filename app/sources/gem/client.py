import json
import requests

from app.sources.gem.constants import (
    DEFAULT_HEADERS,
    LISTING_DATA_URL,
    LISTING_PAGE_URL,
)


class GeMClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _bootstrap_session(self) -> str:
        """
        Load the main all-bids page once so session cookies and CSRF cookie are set.
        Returns the CSRF token value from cookies.
        """
        response = self.session.get(LISTING_PAGE_URL, timeout=30)
        response.raise_for_status()

        csrf_token = self.session.cookies.get("csrf_gem_cookie")
        if not csrf_token:
            raise RuntimeError(
                "Could not find csrf_gem_cookie after loading listing page"
            )

        return csrf_token

    def fetch_listing_data(
        self,
        search_bid: str = "",
        search_type: str = "fullText",
        bid_status_type: str = "ongoing_bids",
        by_type: str = "all",
        high_bid_value: str = "",
        end_date_from: str = "",
        end_date_to: str = "",
        sort: str = "Bid-End-Date-Oldest",
    ) -> dict:
        csrf_token = self._bootstrap_session()

        payload = {
            "param": {
                "searchBid": search_bid,
                "searchType": search_type,
            },
            "filter": {
                "bidStatusType": bid_status_type,
                "byType": by_type,
                "highBidValue": high_bid_value,
                "byEndDate": {
                    "from": end_date_from,
                    "to": end_date_to,
                },
                "sort": sort,
            },
        }

        form_data = {
            "payload": json.dumps(payload, separators=(",", ":")),
            "csrf_bd_gem_nk": csrf_token,
        }

        response = self.session.post(
            LISTING_DATA_URL,
            data=form_data,
            timeout=30,
        )
        response.raise_for_status()

        return response.json()
