from decimal import ROUND_HALF_UP, Decimal
from typing import List

from quote_service.quote import Dimensions, Offer, QuoteRequest, QuoteResponse
from quote_service.rate import Rate
from quote_service.rate_repository import RateRepository


class QuoteService:

  def GetQuote(self, request: QuoteRequest) -> QuoteResponse:
    rate_repository = RateRepository()
    rates = rate_repository.GetRates(request.origin, request.destination, request.shipping_date)

  def CalculateOffers(self, dimensions: Dimensions, rates: List[Rate]) -> List[Offer]:
    # for rate in rates:
    return []

  def CalculateChargeableWeight(self, dimensions: Dimensions) -> float:
    # Decimal from str avoids float artefacts (41.65 stored as 41.6499...) flipping the rounding.
    length, width, height = (
      Decimal(str(side)) for side in (dimensions.length, dimensions.width, dimensions.height)
    )
    volume = length * width * height
    chargeable = max(Decimal(str(dimensions.weight)), volume / 6000)
    return float(chargeable.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))