"""Quote service: input limits and which airlines quote, with an in-memory repository."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from quote_service.errors import InvalidInputError
from quote_service.pricing.shipment import Dimensions, Shipment
from quote_service.rates.rate_repository import InMemoryRateRepository
from quote_service.service import QuoteService

RATE_SHEETS = Path(__file__).parents[2] / "rate_sheets"


def service_with(*airlines: str) -> QuoteService:
    service = QuoteService(InMemoryRateRepository())
    for airline in airlines:
        service.ingest_rate_sheet((RATE_SHEETS / f"{airline}.csv").read_text())
    return service


def shipment(shipping_date: str = "2026-02-10", weight: str = "96", side: str = "10") -> Shipment:
    return Shipment(
        origin="FRA",
        destination="JFK",
        weight_kg=Decimal(weight),
        dimensions=Dimensions(Decimal(side), Decimal(side), Decimal(side)),
        shipping_date=date.fromisoformat(shipping_date),
    )


@pytest.mark.parametrize(
    "weight, side, message",
    [
        ("100001", "10", "weight must be <= 100000"),
        ("96", "10001", "length must be <= 10000"),
        ("1E+26", "10", "weight must be <= 100000"),
    ],
)
def test_measures_above_the_limits_are_rejected(weight, side, message):
    # given a shipment heavier or larger than any real air cargo shipment
    service = service_with("LH")

    # when it is quoted
    with pytest.raises(InvalidInputError) as err:
        service.get_quote(shipment(weight=weight, side=side))

    # then it is rejected instead of overflowing the rounding
    assert message in str(err.value)


def test_measures_on_the_limits_are_quoted():
    # given a shipment exactly on the weight and size limits
    service = service_with("LH")

    # when it is quoted
    offers = service.get_quote(shipment(weight="100000", side="10000"))

    # then LH quotes it
    assert [offer.airline for offer in offers] == ["LH"]


def test_airlines_without_a_valid_rate_get_no_offer():
    # given all 4 sample sheets, where QR's FRA-JFK rate ends on 2026-02-28
    service = service_with("LH", "AF", "EK", "QR")

    # when FRA-JFK is quoted on 2026-03-01
    offers = service.get_quote(shipment(shipping_date="2026-03-01", weight="80"))

    # then QR is left out and the other airlines still quote
    assert sorted(offer.airline for offer in offers) == ["AF", "EK", "LH"]
