from typing import List

class Dimensions:
  weight: float
  width: int
  height: int
  length: int
class QuoteRequest:
  origin: str
  destination: str
  dimensions: Dimensions
  shipping_date: str

class Offer:
  airline: str
  currency: str
  chargeable_weight_kg: float
  weight_break: str
  rate_per_kg: float
  total_price: float

class QuoteResponse:
  offers: List[Offer]
