from datetime import datetime, timezone, timedelta

def get_utc_now() -> datetime:
    """Returns current UTC datetime with timezone info."""
    return datetime.now(timezone.utc)

def format_iso8601(dt: datetime) -> str:
    """Formats datetime as ISO8601 string."""
    return dt.isoformat()

def parse_iso8601(iso_str: str) -> datetime:
    """Parses ISO8601 string to datetime."""
    return datetime.fromisoformat(iso_str)

def is_expired(expires_at_str: str) -> bool:
    """Checks whether the given ISO8601 timestamp string has passed."""
    exp_dt = parse_iso8601(expires_at_str)
    return get_utc_now() > exp_dt
