"""
Time utilities for consistent local time handling
"""
from datetime import datetime, timezone, timedelta

# Indonesia timezone offset (UTC+7)
INDONESIA_OFFSET = timezone(timedelta(hours=7))

def get_local_now() -> datetime:
    """
    Get current datetime in Indonesia local time (UTC+7)
    Returns timezone-aware datetime object
    """
    return datetime.now(INDONESIA_OFFSET)

def get_local_naive_now() -> datetime:
    """
    Get current datetime in Indonesia local time as naive datetime
    (without timezone info, for database storage)
    """
    local_time = get_local_now()
    return local_time.replace(tzinfo=None)

def utc_to_local(utc_dt: datetime) -> datetime:
    """
    Convert UTC datetime to Indonesia local time
    """
    if utc_dt.tzinfo is None:
        # Assume UTC if no timezone info
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    return utc_dt.astimezone(INDONESIA_OFFSET)

def local_to_utc(local_dt: datetime) -> datetime:
    """
    Convert Indonesia local time to UTC
    """
    if local_dt.tzinfo is None:
        # Assume local time if no timezone info
        local_dt = local_dt.replace(tzinfo=INDONESIA_OFFSET)
    
    return local_dt.astimezone(timezone.utc)
