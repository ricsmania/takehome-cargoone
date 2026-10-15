"""Turns rate rows into offers: weight breaks, as-agreed rating, min charge. Pure, no I/O."""

from decimal import ROUND_HALF_UP, Decimal

from quote_service.domain.offer import Offer
from quote_service.domain.rate import Rate
from quote_service.domain.shipment import Shipment
from quote_service.rating.chargeable_weight import calculate_chargeable_weight


def calculate_best_offer_per_airline(shipment: Shipment, rates: list[Rate]) -> list[Offer]:
    chargeable_weight = calculate_chargeable_weight(shipment.weight_kg, shipment.dimensions)

    # One offer per airline. When an airline has several applicable rows (overlapping
    # validity windows), keep the cheapest.
    best_by_airline: dict[str, Offer] = {}
    for rate in rates:
        offer = calculate_offer_for_rate(chargeable_weight, rate)
        current = best_by_airline.get(rate.airline)
        if current is None or offer.total_price < current.total_price:
            best_by_airline[rate.airline] = offer

    # Airline as the last key only makes the order deterministic when totals tie.
    return sorted(
        best_by_airline.values(),
        key=lambda offer: (offer.currency, offer.total_price, offer.airline),
    )


def calculate_offer_for_rate(chargeable_weight: Decimal, rate: Rate) -> Offer:
    breaks = weight_breaks(rate)

    # Start with the break that contains the chargeable weight: the last one whose
    # minimum is not above it.
    start = max(i for i, (_, minimum_kg, _) in enumerate(breaks) if minimum_kg <= chargeable_weight)
    best_break, _, best_rate = breaks[start]
    best_total = chargeable_weight * best_rate

    # As-agreed rating: a higher break priced at its own minimum weight wins if cheaper.
    # On a tie the lower break is kept.
    for name, minimum_kg, rate_per_kg in breaks[start + 1 :]:
        total = minimum_kg * rate_per_kg
        if total < best_total:
            best_break, best_rate, best_total = name, rate_per_kg, total

    total_price = max(best_total, rate.min_charge)
    return Offer(
        airline=rate.airline,
        currency=rate.currency,
        chargeable_weight_kg=chargeable_weight,
        weight_break=best_break,
        rate_per_kg=best_rate,
        total_price=total_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
    )


def weight_breaks(rate: Rate) -> list[tuple[str, Decimal, Decimal]]:
    """(name, minimum weight in kg, rate per kg) for each break, lowest first."""
    return [
        ("normal", Decimal(0), rate.rate_normal),
        ("45", Decimal(45), rate.rate_45),
        ("100", Decimal(100), rate.rate_100),
        ("300", Decimal(300), rate.rate_300),
        ("500", Decimal(500), rate.rate_500),
    ]
