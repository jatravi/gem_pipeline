class GeMListingParser:
    def parse_listing_docs(self, payload: dict) -> list[dict]:
        docs = (
            payload.get("response", {})
            .get("response", {})
            .get("docs", [])
        )

        parsed = []
        for doc in docs:
            raw_bid = self._parse_doc(doc)
            if raw_bid:
                parsed.append(raw_bid)

        return parsed

    def _parse_doc(self, doc: dict) -> dict | None:
        bid_number = self._first(doc.get("b_bid_number_parent"))
        ra_number = self._first(doc.get("b_bid_number"))

        if not bid_number:
            return None

        return {
            "bid_number": bid_number,
            "ra_number": ra_number,
            "title": self._first(doc.get("b_category_name")) or self._first(doc.get("bd_category_name")),
            "ministry": self._first(doc.get("ba_official_details_minName")),
            "department": self._first(doc.get("ba_official_details_deptName")),
            "organisation": None,
            "office": None,
            "start_date_text": self._first(doc.get("final_start_date_sort")),
            "closing_date_text": self._first(doc.get("final_end_date_sort")),
            "estimated_value": None,
            "emd_amount": None,
            "status_code": self._first(doc.get("b_status")),
            "source_url": "https://bidplus.gem.gov.in/all-bids",
            "raw_doc": doc,
        }

    def _first(self, value):
        if isinstance(value, list) and value:
            return value[0]
        return value