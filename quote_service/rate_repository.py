from typing import List

from quote_service.rate import Rate


class RateRepository:
  def GetRates(origin: str, destination: str, shipping_date: str) -> List[Rate]:
    return    