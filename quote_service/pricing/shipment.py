"""The shipment to quote and the offers returned for it."""

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


@dataclass(frozen=True)
class Offer:
    airline: str
    currency: str
    chargeable_weight_kg: Decimal
    weight_break: str
    rate_per_kg: Decimal
    total_price: Decimal
