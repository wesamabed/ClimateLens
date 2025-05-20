# etl/transformer/utils.py

def strip_flag(v: str) -> str:
    """
    Remove any non-digit or dot from a string,
    e.g. "24G" → "24", "-99.9*" → "-99.9"
    """
    return "".join(ch for ch in v if ch.isdigit() or ch in ".-")
