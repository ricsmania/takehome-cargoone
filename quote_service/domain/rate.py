"""One row of an airline rate sheet: a lane, a validity window and its prices."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Rate:
    airline: str
    origin: str
    destination: str
    currency: str
    valid_from: date  # inclusive
    valid_to: date  # inclusive
    min_charge: Decimal
    rate_normal: Decimal
    rate_45: Decimal
    rate_100: Decimal
    rate_300: Decimal
    rate_500: Decimal
