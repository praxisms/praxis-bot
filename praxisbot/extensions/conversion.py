from typing import Any, Optional


def int_or_none(value: Any) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None
