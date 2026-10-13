from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal
from typing import List

from quote_service.quote import Dimensions, Offer, QuoteRequest, QuoteResponse
from quote_service.rate import Rate
from quote_service.rate_repository import RateRepository


class QuoteService:

  def GetQuote(self, request: QuoteRequest) -> QuoteResponse:
    rate_repository = RateRepository()
    rates = rate_repository.GetRates(request.origin, request.destination, request.shipping_date)

  def CalculateOffers(self, dimensions: Dimensions, rates: List[Rate]) -> List[Offer]:
    chargeable_weight = Decimal(str(self.CalculateChargeableWeight(dimensions)))

    # One offer per airline. When an airline has several applicable rows (overlapping
    # validity windows), keep the cheapest.
    best_by_airline: dict[str, Offer] = {}
    for rate in rates:
      offer = self.CalculateOffer(chargeable_weight, rate)
      current = best_by_airline.get(rate.airline)
      if current is None or offer.total_price < current.total_price:
        best_by_airline[rate.airline] = offer

    # Airline as the last key only makes the order deterministic when totals tie.
    return sorted(
      best_by_airline.values(),
      key=lambda offer: (offer.currency, offer.total_price, offer.airline),
    )

  def CalculateOffer(self, chargeable_weight: Decimal, rate: Rate) -> Offer:
    breaks = self.WeightBreaks(rate)

    # Start with the break that contains the chargeable weight: the last one whose
    # minimum is not above it.
    start = max(i for i, (_, minimum_kg, _) in enumerate(breaks) if minimum_kg <= chargeable_weight)
    best_break, _, best_rate = breaks[start]
    best_total = chargeable_weight * best_rate

    # As-agreed rating: a higher break priced at its own minimum weight wins if cheaper.
    # On a tie the lower break is kept.
    for name, minimum_kg, rate_per_kg in breaks[start + 1:]:
      total = minimum_kg * rate_per_kg
      if total < best_total:
        best_break, best_rate, best_total = name, rate_per_kg, total

    total_price = max(best_total, Decimal(str(rate.min_charge)))
    return Offer(
      airline=rate.airline,
      currency=rate.currency,
      chargeable_weight_kg=float(chargeable_weight),
      weight_break=best_break,
      rate_per_kg=float(best_rate),
      total_price=float(total_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
    )

  def WeightBreaks(self, rate: Rate) -> list[tuple[str, Decimal, Decimal]]:
    """(name, minimum weight in kg, rate per kg) for each break, lowest first."""
    return [
      ("normal", Decimal(0), Decimal(str(rate.rate_normal))),
      ("45", Decimal(45), Decimal(str(rate.rate_45))),
      ("100", Decimal(100), Decimal(str(rate.rate_100))),
      ("300", Decimal(300), Decimal(str(rate.rate_300))),
      ("500", Decimal(500), Decimal(str(rate.rate_500))),
    ]

  def CalculateChargeableWeight(self, dimensions: Dimensions) -> float:
    # Both round up, so we never charge for less than the shipment weighs or measures.
    # Decimal from str avoids float artefacts (96.8 stored as 96.80000001) adding an extra 0.1 kg.
    length, width, height = (
      Decimal(str(side)).quantize(Decimal(1), rounding=ROUND_CEILING)
      for side in (dimensions.length, dimensions.width, dimensions.height)
    )
    volumetric = length * width * height / 6000
    chargeable = max(Decimal(str(dimensions.weight)), volumetric)
    return float(chargeable.quantize(Decimal("0.1"), rounding=ROUND_CEILING))
