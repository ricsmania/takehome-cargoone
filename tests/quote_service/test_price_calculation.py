"""README worked examples: FRA-JFK on 2026-02-10, with the 4 sample sheets' applicable rows."""


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
# Reversed, so the expected order can only come from sorting, not from the input order.
ALL_RATES = [QR, EK, AF, LH]


def offer_lines(dimensions: Dimensions, rates: list[Rate]) -> list[tuple]:
    """Offers as (airline, currency, weight_break, total) lines, in the order returned."""
    offers = QuoteService().CalculateOffers(dimensions, rates)
    return [
        (offer.airline, offer.currency, offer.weight_break, round(offer.total_price, 2))
        for offer in offers
    ]


def test_96_kg_volumetric_shipment_lands_on_100_break():
    # given an 80 kg, 120 x 80 x 60 cm shipment (96 kg volumetric, so 96 kg chargeable)
    dimensions = Dimensions(weight=80, length=120, width=80, height=60)

    # when offers are calculated against all 4 sample rows
    lines = offer_lines(dimensions, ALL_RATES)

    # then the 100 break priced at 100 kg beats the 45 break at 96 kg for every airline,
    # one line per airline, sorted by currency and then by price
    assert lines == [
        ("LH", "EUR", "100", 340.00),
        ("AF", "EUR", "100", 365.00),
        ("EK", "USD", "100", 320.00),
        ("QR", "USD", "100", 360.00),
    ]


def test_75_kg_shipment_break_differs_per_airline():
    # given a 75 kg, 10 x 10 x 10 cm shipment (actual weight is chargeable)
    dimensions = Dimensions(weight=75, length=10, width=10, height=10)

    # when offers are calculated against all 4 sample rows
    lines = offer_lines(dimensions, ALL_RATES)

    # then only EK is cheaper at the higher break
    assert lines == [
        ("LH", "EUR", "45", 285.00),   # 75 x 3.80, the 100 break is 340.00
        ("AF", "EUR", "45", 303.75),   # 75 x 4.05, the 100 break is 365.00
        ("EK", "USD", "100", 320.00),  # 75 x 4.60 = 345.00, the 100 break is 100 x 3.20
        ("QR", "USD", "45", 322.50),   # 75 x 4.30, the 100 break is 360.00
    ]


def test_small_shipment_is_raised_to_min_charge():
    # given a 5 kg, 20 x 20 x 20 cm shipment (5 kg chargeable, 5 x 4.10 = 20.50 EUR)
    dimensions = Dimensions(weight=5, length=20, width=20, height=20)

    # when the LH offer is calculated
    lines = offer_lines(dimensions, [LH])

    # then the total is LH's min_charge
    assert lines == [("LH", "EUR", "normal", 90.00)]
