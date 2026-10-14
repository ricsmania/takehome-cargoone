"""README worked examples: FRA-JFK on 2026-02-10, with the 4 sample sheets' applicable rows."""

from datetime import date
from decimal import Decimal

from quote_service.pricing import calculate_offers
from quote_service.quote import Dimensions, Shipment
from quote_service.rate import Rate


def rate(airline: str, currency: str, valid_from: str, valid_to: str, min_charge: str,
         normal: str, r45: str, r100: str, r300: str, r500: str) -> Rate:
    return Rate(airline=airline, origin="FRA", destination="JFK", currency=currency,
                valid_from=date.fromisoformat(valid_from), valid_to=date.fromisoformat(valid_to),
                min_charge=Decimal(min_charge), rate_normal=Decimal(normal), rate_45=Decimal(r45),
                rate_100=Decimal(r100), rate_300=Decimal(r300), rate_500=Decimal(r500))


# The FRA-JFK row from each sample sheet that is valid on 2026-02-10.
LH = rate("LH", "EUR", "2026-01-01", "2026-03-31", "90.00", "4.10", "3.80", "3.40", "2.95", "2.60")
AF = rate("AF", "EUR", "2026-01-01", "2026-06-30", "100.00", "4.40", "4.05", "3.65", "3.15", "2.80")
EK = rate("EK", "USD", "2026-01-01", "2026-12-31", "150.00", "5.20", "4.60", "3.20", "2.80", "2.40")
QR = rate("QR", "USD", "2026-01-15", "2026-02-28", "120.00", "4.80", "4.30", "3.60", "3.10", "2.70")
# Reversed, so the expected order can only come from sorting, not from the input order.
ALL_RATES = [QR, EK, AF, LH]


def shipment(weight: str, length: str, width: str, height: str) -> Shipment:
    return Shipment(
        origin="FRA",
        destination="JFK",
        weight_kg=Decimal(weight),
        dimensions=Dimensions(Decimal(length), Decimal(width), Decimal(height)),
        shipping_date=date(2026, 2, 10),
    )


def offer_lines(to_quote: Shipment, rates: list[Rate]) -> list[tuple]:
    """Offers as (airline, currency, weight_break, total) lines, in the order returned."""
    offers = calculate_offers(to_quote, rates)
    return [
        (offer.airline, offer.currency, offer.weight_break, str(offer.total_price))
        for offer in offers
    ]


def test_96_kg_volumetric_shipment_lands_on_100_break():
    # given an 80 kg, 120 x 80 x 60 cm shipment (96 kg volumetric, so 96 kg chargeable)
    to_quote = shipment("80", "120", "80", "60")

    # when offers are calculated against all 4 sample rows
    lines = offer_lines(to_quote, ALL_RATES)

    # then the 100 break priced at 100 kg beats the 45 break at 96 kg for every airline,
    # one line per airline, sorted by currency and then by price
    assert lines == [
        ("LH", "EUR", "100", "340.00"),
        ("AF", "EUR", "100", "365.00"),
        ("EK", "USD", "100", "320.00"),
        ("QR", "USD", "100", "360.00"),
    ]


def test_75_kg_shipment_break_differs_per_airline():
    # given a 75 kg, 10 x 10 x 10 cm shipment (actual weight is chargeable)
    to_quote = shipment("75", "10", "10", "10")

    # when offers are calculated against all 4 sample rows
    lines = offer_lines(to_quote, ALL_RATES)

    # then only EK is cheaper at the higher break
    assert lines == [
        ("LH", "EUR", "45", "285.00"),   # 75 x 3.80, the 100 break is 340.00
        ("AF", "EUR", "45", "303.75"),   # 75 x 4.05, the 100 break is 365.00
        ("EK", "USD", "100", "320.00"),  # 75 x 4.60 = 345.00, the 100 break is 100 x 3.20
        ("QR", "USD", "45", "322.50"),   # 75 x 4.30, the 100 break is 360.00
    ]


def test_small_shipment_is_raised_to_min_charge():
    # given a 5 kg, 20 x 20 x 20 cm shipment (5 kg chargeable, 5 x 4.10 = 20.50 EUR)
    to_quote = shipment("5", "20", "20", "20")

    # when the LH offer is calculated
    lines = offer_lines(to_quote, [LH])

    # then the total is LH's min_charge
    assert lines == [("LH", "EUR", "normal", "90.00")]
