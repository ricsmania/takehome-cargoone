from typing import List

from quote_service.rate import Rate


class RateRepository:
  def GetRates(self, origin: str, destination: str, shipping_date: str) -> List[Rate]:
    return    