from datetime import datetime


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    value = value.strip()
    formats = [
        "%d-%m-%Y %I:%M %p",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%dT%H:%M:%SZ",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None
