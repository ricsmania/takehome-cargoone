"""One airline's offer for a shipment."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Offer:
    airline: str
    currency: str
    chargeable_weight_kg: Decimal
    weight_break: str
    rate_per_kg: Decimal
    total_price: Decimal
