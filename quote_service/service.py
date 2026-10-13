from typing import List

from quote_service.quote import Dimensions, Offer, QuoteRequest, QuoteResponse
from quote_service.rate import Rate
from quote_service.rate_repository import RateRepository


class QuoteService:

  def GetQuote(request: QuoteRequest) -> QuoteResponse:
    rate_repository = RateRepository()
    rates = rate_repository.GetRates(request.origin, request.destination, request.shipping_date)

  def CalculateOffers(dimensions: Dimensions, rates: List[Rate]) -> List[Offer]:
    # for rate in rates:
    return 
