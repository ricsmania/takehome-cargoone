"""README worked examples: FRA-JFK on 2026-02-10, with the 4 sample sheets' applicable rows."""

import pytest

from quote_service.quote import Dimensions
from quote_service.rate import Rate
from quote_service.service import QuoteService

# The FRA-JFK row from each sample sheet that is valid on 2026-02-10.
LH = Rate(airline="LH", origin="FRA", destination="JFK", currency="EUR",
          valid_from="2026-01-01", valid_to="2026-03-31", min_charge=90.00,
          rate_normal=4.10, rate_45=3.80, rate_100=3.40, rate_300=2.95, rate_500=2.60)
AF = Rate(airline="AF", origin="FRA", destination="JFK", currency="EUR",
          valid_from="2026-01-01", valid_to="2026-06-30", min_charge=100.00,
          rate_normal=4.40, rate_45=4.05, rate_100=3.65, rate_300=3.15, rate_500=2.80)
EK = Rate(airline="EK", origin="FRA", destination="JFK", currency="USD",
          valid_from="2026-01-01", valid_to="2026-12-31", min_charge=150.00,
          rate_normal=5.20, rate_45=4.60, rate_100=3.20, rate_300=2.80, rate_500=2.40)
QR = Rate(airline="QR", origin="FRA", destination="JFK", currency="USD",
          valid_from="2026-01-15", valid_to="2026-02-28", min_charge=120.00,
          rate_normal=4.80, rate_45=4.30, rate_100=3.60, rate_300=3.10, rate_500=2.70)
ALL_RATES = [LH, AF, EK, QR]


def offers_by_airline(dimensions: Dimensions, rates: list[Rate]) -> dict:
    offers = QuoteService().CalculateOffers(dimensions, rates)
    return {offer.airline: offer for offer in offers}


@pytest.mark.parametrize(
    "airline, total, currency, weight_break",
    [
        ("LH", 340.00, "EUR", "100"),
        ("AF", 365.00, "EUR", "100"),
        ("EK", 320.00, "USD", "100"),
        ("QR", 360.00, "USD", "100"),
    ],
)
def test_96_kg_volumetric_shipment_lands_on_100_break(airline, total, currency, weight_break):
    # given an 80 kg, 120 x 80 x 60 cm shipment (96 kg volumetric, so 96 kg chargeable)
    dimensions = Dimensions(weight=80, length=120, width=80, height=60)

    # when offers are calculated against all 4 sample rows
    offers = offers_by_airline(dimensions, ALL_RATES)

    # then the 100 break priced at 100 kg beats the 45 break at 96 kg for every airline
    offer = offers[airline]
    assert offer.total_price == pytest.approx(total)
    assert offer.currency == currency
    assert offer.weight_break == weight_break


@pytest.mark.parametrize(
    "airline, total, currency, weight_break",
    [
        ("LH", 285.00, "EUR", "45"),   # 75 x 3.80, the 100 break is 340.00
        ("AF", 303.75, "EUR", "45"),   # 75 x 4.05, the 100 break is 365.00
        ("EK", 320.00, "USD", "100"),  # 75 x 4.60 = 345.00, the 100 break is 100 x 3.20
        ("QR", 322.50, "USD", "45"),   # 75 x 4.30, the 100 break is 360.00
    ],
)
def test_75_kg_shipment_break_differs_per_airline(airline, total, currency, weight_break):
    # given a 75 kg, 10 x 10 x 10 cm shipment (actual weight is chargeable)
    dimensions = Dimensions(weight=75, length=10, width=10, height=10)

    # when offers are calculated against all 4 sample rows
    offers = offers_by_airline(dimensions, ALL_RATES)

    # then only EK is cheaper at the higher break
    offer = offers[airline]
    assert offer.total_price == pytest.approx(total)
    assert offer.currency == currency
    assert offer.weight_break == weight_break


def test_returns_one_offer_per_airline():
    # given the 4 sample rows, one per airline
    dimensions = Dimensions(weight=80, length=120, width=80, height=60)

    # when offers are calculated
    offers = QuoteService().CalculateOffers(dimensions, ALL_RATES)

    # then there is exactly one offer for each airline
    assert sorted(offer.airline for offer in offers) == ["AF", "EK", "LH", "QR"]


def test_small_shipment_is_raised_to_min_charge():
    # given a 5 kg, 20 x 20 x 20 cm shipment (5 kg chargeable, 5 x 4.10 = 20.50 EUR)
    dimensions = Dimensions(weight=5, length=20, width=20, height=20)

    # when the LH offer is calculated
    offers = offers_by_airline(dimensions, [LH])

    # then the total is LH's min_charge
    assert offers["LH"].total_price == pytest.approx(90.00)
    assert offers["LH"].currency == "EUR"
