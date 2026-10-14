"""Codes the service accepts, in rate sheets and in quote requests."""

import re

# Format check only: any 3 uppercase letters pass, whether or not the airport exists.
AIRPORT_CODE = re.compile(r"[A-Z]{3}")  # IATA airport code, e.g. FRA

CURRENCIES = frozenset({"EUR", "USD"})


def is_airport_code(value: str) -> bool:
    return AIRPORT_CODE.fullmatch(value) is not None
