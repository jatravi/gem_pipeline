from app.schemas.bid import ParsedBid
from app.utils.dates import parse_datetime


class GeMBidNormalizer:
    def normalize(self, raw_bid: dict) -> ParsedBid | None:
        bid_number = raw_bid.get("bid_number")
        if not bid_number:
            return None

        status_code = raw_bid.get("status_code")
        status = self._map_status(status_code)

        return ParsedBid(
            bid_number=bid_number,
            ra_number=raw_bid.get("ra_number"),
            title=raw_bid.get("title"),
            ministry=raw_bid.get("ministry"),
            department=raw_bid.get("department"),
            organisation=raw_bid.get("organisation"),
            office=raw_bid.get("office"),
            start_date=parse_datetime(raw_bid.get("start_date_text")),
            closing_date=parse_datetime(raw_bid.get("closing_date_text")),
            estimated_value=raw_bid.get("estimated_value"),
            emd_amount=raw_bid.get("emd_amount"),
            status=status,
            source_url=raw_bid.get("source_url"),
        )

    def _map_status(self, status_code) -> str | None:
        mapping = {
            1: "active",
            0: "inactive",
        }
        return mapping.get(status_code, str(status_code) if status_code is not None else None)