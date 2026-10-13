from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Dimensions:
  weight: float
  width: int
  height: int
  length: int


@dataclass(frozen=True)
class QuoteRequest:
  origin: str
  destination: str
  dimensions: Dimensions
  shipping_date: str


@dataclass(frozen=True)
class Offer:
  airline: str
  currency: str
  chargeable_weight_kg: float
  weight_break: str
  rate_per_kg: float
  total_price: float


@dataclass(frozen=True)
class QuoteResponse:
  offers: List[Offer]
