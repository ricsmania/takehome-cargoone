from decimal import ROUND_CEILING, Decimal
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
    # Both round up, so we never charge for less than the shipment weighs or measures.
    # Decimal from str avoids float artefacts (96.8 stored as 96.80000001) adding an extra 0.1 kg.
    length, width, height = (
      Decimal(str(side)).quantize(Decimal("1"), rounding=ROUND_CEILING)
      for side in (dimensions.length, dimensions.width, dimensions.height)
    )
    volumetric = length * width * height / 6000
    chargeable = max(Decimal(str(dimensions.weight)), volumetric)
    return float(chargeable.quantize(Decimal("0.1"), rounding=ROUND_CEILING))
