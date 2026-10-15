"""The shipment to quote."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Dimensions:
    length_cm: Decimal
    width_cm: Decimal
    height_cm: Decimal


@dataclass(frozen=True)
class Shipment:
    origin: str
    destination: str
    weight_kg: Decimal
    dimensions: Dimensions
    shipping_date: date
