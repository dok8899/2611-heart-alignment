from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def format_utc(value: datetime | None = None) -> str:
    current = value or utc_now()
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
