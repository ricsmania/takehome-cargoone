from typing import List

from quote_service.rate import Rate


class RateRepository:
  def get_rates(self, origin: str, destination: str, shipping_date: str) -> List[Rate]:
    """Rates for the lane whose validity window contains shipping_date (both ends inclusive)."""
    return    