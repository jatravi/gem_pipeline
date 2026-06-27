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
        parent_bid_number = self._first(doc.get("b_bid_number_parent"))
        current_bid_number = self._first(doc.get("b_bid_number"))

        bid_number = parent_bid_number or current_bid_number
        ra_number = current_bid_number if parent_bid_number else None

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
            "source_bid_id": str(self._first(doc.get("b_id")) or doc.get("id")),
            "parent_source_bid_id": (
                str(self._first(doc.get("b_id_parent")))
                if self._first(doc.get("b_id_parent")) is not None
                else None
            ),
            "raw_listing_payload": doc,
        }

    def _first(self, value):
        if isinstance(value, list) and value:
            return value[0]
        return value