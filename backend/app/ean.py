"""EAN rules shared by API lookup and curated-data validation."""
import re


def is_valid_ean(ean: str) -> bool:
    """Accept EAN-8 or EAN-13 with a correct check digit."""
    if not re.fullmatch(r"(?:[0-9]{8}|[0-9]{13})", ean):
        return False
    total = sum(int(digit) * (3 if index % 2 == 0 else 1)
                for index, digit in enumerate(reversed(ean[:-1])))
    return (10 - total % 10) % 10 == int(ean[-1])
