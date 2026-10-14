from quote_service.quote import QuoteRequest, QuoteResponse
from quote_service.rate_repository import RateRepository


class QuoteService:

  def get_quote(self, request: QuoteRequest) -> QuoteResponse:
    rate_repository = RateRepository()
    rates = rate_repository.get_rates(request.origin, request.destination, request.shipping_date)
