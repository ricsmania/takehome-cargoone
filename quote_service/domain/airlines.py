"""Airline codes the service accepts in rate sheets."""

import re

# Format check only: any 2 uppercase letters or digits pass, whether or not the airline exists.
AIRLINE_CODE = re.compile(r"[A-Z0-9]{2}")  # IATA airline designator, e.g. LH


def is_airline_code(value: str) -> bool:
    return AIRLINE_CODE.fullmatch(value) is not None
