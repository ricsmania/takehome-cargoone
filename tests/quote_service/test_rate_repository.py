"""In-memory repository: lookup by lane, replacement per airline."""

from datetime import date
from decimal import Decimal

from quote_service.rate import Rate
from quote_service.rate_repository import InMemoryRateRepository


def rate(airline: str, origin: str, destination: str, valid_from: str, valid_to: str) -> Rate:
    """A rate whose prices do not matter to the lookup."""
    price = Decimal("1.00")
    return Rate(airline=airline, origin=origin, destination=destination, currency="EUR",
                valid_from=date.fromisoformat(valid_from), valid_to=date.fromisoformat(valid_to),
                min_charge=price, rate_normal=price, rate_45=price, rate_100=price,
                rate_300=price, rate_500=price)


QR_FRA_JFK = rate("QR", "FRA", "JFK", "2026-01-15", "2026-02-28")


def test_lanes_have_a_direction():
    # given only a FRA-JFK row
    repository = InMemoryRateRepository()
    repository.replace_airline_rates("QR", [QR_FRA_JFK])

    # when JFK-FRA is looked up
    rates = repository.get_rates("JFK", "FRA")

    # then nothing is found
    assert rates == []


def test_every_row_of_the_lane_is_returned():
    # given AF's 2 CDG-JFK rows, with overlapping windows, and a CDG-ORD row
    half_year = rate("AF", "CDG", "JFK", "2026-01-01", "2026-06-30")
    march = rate("AF", "CDG", "JFK", "2026-03-01", "2026-03-31")
    other_lane = rate("AF", "CDG", "ORD", "2026-01-01", "2026-06-30")
    repository = InMemoryRateRepository()
    repository.replace_airline_rates("AF", [half_year, march, other_lane])

    # when CDG-JFK is looked up
    rates = repository.get_rates("CDG", "JFK")

    # then both CDG-JFK rows are returned, whatever their windows
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

    # then the old LH row is gone and QR is untouched
    assert repository.get_rates("FRA", "JFK") == [new_lh, QR_FRA_JFK]
