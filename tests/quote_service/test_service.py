"""Quote service: validity windows and input limits, with an in-memory repository."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from quote_service.errors import InvalidInputError
from quote_service.quote import Dimensions, Shipment
from quote_service.rate_repository import InMemoryRateRepository
from quote_service.service import QuoteService

RATE_SHEETS = Path(__file__).parents[2] / "rate_sheets"


def service_with(*airlines: str) -> QuoteService:
    service = QuoteService(InMemoryRateRepository())
    for airline in airlines:
        service.ingest_rate_sheet((RATE_SHEETS / f"{airline}.csv").read_text())
    return service


def shipment(shipping_date: str = "2026-02-10", weight: str = "96",
             side: str = "10") -> Shipment:
    return Shipment(
        origin="FRA",
        destination="JFK",
        weight_kg=Decimal(weight),
        dimensions=Dimensions(Decimal(side), Decimal(side), Decimal(side)),
        shipping_date=date.fromisoformat(shipping_date),
    )


@pytest.mark.parametrize("shipping_date, has_offer", [
    ("2026-01-14", False),
    ("2026-01-15", True),
    ("2026-02-28", True),
    ("2026-03-01", False),
])
def test_validity_window_includes_both_ends(shipping_date, has_offer):
    # given the QR sheet, whose FRA-JFK row is valid 2026-01-15 to 2026-02-28
    service = service_with("QR")

    # when FRA-JFK is quoted on a date around the window's ends
    offers = service.get_quote(shipment(shipping_date))

    # then QR quotes only inside the window, ends included
    assert (len(offers) == 1) == has_offer


@pytest.mark.parametrize("weight, side, message", [
    ("100001", "10", "weight must be <= 100000"),
    ("96", "10001", "length must be <= 10000"),
    ("1E+26", "10", "weight must be <= 100000"),
])
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
