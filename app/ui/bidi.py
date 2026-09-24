"""Bidirectional-text helpers (blueprint §3.3)."""

LRI, PDI = "\u2066", "\u2069"


def ltr(text: str) -> str:
    """Isolate an LTR fragment (numbers + units, code-ish tokens) inside RTL text."""
    return f"{LRI}{text}{PDI}"
