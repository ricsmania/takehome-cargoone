"""In-memory repository: lane and validity-window lookup, replacement per airline."""

from datetime import date
from decimal import Decimal

import pytest

from quote_service.rate import Rate
from quote_service.rate_repository import InMemoryRateRepository


def rate(airline: str, origin: str, destination: str, valid_from: str, valid_to: str) -> Rate:
    """A rate whose prices do not matter to the lookup."""
    price = Decimal("1.00")
    return Rate(airline=airline, origin=origin, destination=destination, currency="EUR",
                valid_from=date.fromisoformat(valid_from), valid_to=date.fromisoformat(valid_to),
                min_charge=price, rate_normal=price, rate_45=price, rate_100=price,
                rate_300=price, rate_500=price)


# QR's FRA-JFK row from the sample sheet.
QR_FRA_JFK = rate("QR", "FRA", "JFK", "2026-01-15", "2026-02-28")


@pytest.mark.parametrize("shipping_date, found", [
    ("2026-01-14", False),
    ("2026-01-15", True),
    ("2026-02-28", True),
    ("2026-03-01", False),
])
def test_validity_window_includes_both_ends(shipping_date, found):
    # given QR's FRA-JFK row, valid 2026-01-15 to 2026-02-28
    repository = InMemoryRateRepository()
    repository.replace_airline_rates("QR", [QR_FRA_JFK])

    # when FRA-JFK rates are looked up around the window's ends
    rates = repository.get_rates("FRA", "JFK", date.fromisoformat(shipping_date))

    # then the row is found only inside the window, ends included
    assert (rates == [QR_FRA_JFK]) == found


def test_lanes_have_a_direction():
    # given only a FRA-JFK row
    repository = InMemoryRateRepository()
    repository.replace_airline_rates("QR", [QR_FRA_JFK])

    # when JFK-FRA is looked up on a date inside the window
    rates = repository.get_rates("JFK", "FRA", date(2026, 2, 10))

    # then nothing is found
    assert rates == []


def test_overlapping_rows_are_all_returned():
    # given AF's 2 CDG-JFK rows, which both cover 2026-03-01
    half_year = rate("AF", "CDG", "JFK", "2026-01-01", "2026-06-30")
    march = rate("AF", "CDG", "JFK", "2026-03-01", "2026-03-31")
    repository = InMemoryRateRepository()
    repository.replace_airline_rates("AF", [half_year, march])

    # when CDG-JFK is looked up on 2026-03-01
    rates = repository.get_rates("CDG", "JFK", date(2026, 3, 1))

    # then both are returned, so rating can pick the cheapest
    assert rates == [half_year, march]


def test_replacing_an_airline_drops_its_old_rates_only():
    # given LH and QR rates on FRA-JFK
    old_lh = rate("LH", "FRA", "JFK", "2026-01-01", "2026-03-31")
    repository = InMemoryRateRepository()
    repository.replace_airline_rates("LH", [old_lh])
    repository.replace_airline_rates("QR", [QR_FRA_JFK])

    # when LH's rates are replaced by a row for April to June
    new_lh = rate("LH", "FRA", "JFK", "2026-04-01", "2026-06-30")
    repository.replace_airline_rates("LH", [new_lh])

    # then the old LH row is gone on 2026-02-10 and QR is untouched
    assert repository.get_rates("FRA", "JFK", date(2026, 2, 10)) == [QR_FRA_JFK]
    assert repository.get_rates("FRA", "JFK", date(2026, 5, 1)) == [new_lh]
