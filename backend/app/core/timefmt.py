from datetime import datetime
from typing import Optional


def fmt(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")
