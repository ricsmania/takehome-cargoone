"""The two RPCs end to end: wiring, status codes and a few complete quotes.

The rules themselves are unit-tested next to the code that applies them."""

from pathlib import Path

import grpc
import pytest

from proto import quote_pb2

RATE_SHEETS = Path(__file__).parents[1] / "rate_sheets"
SAMPLE_AIRLINES = ["LH", "AF", "EK", "QR"]


def ingest(stub, csv_content: str) -> int:
    request = quote_pb2.IngestRateSheetRequest(csv_content=csv_content)
    return stub.IngestRateSheet(request).rows_ingested


def ingest_samples(stub) -> None:
    for airline in SAMPLE_AIRLINES:
        ingest(stub, (RATE_SHEETS / f"{airline}.csv").read_text())


def quote(
    stub,
    origin: str,
    destination: str,
    weight: float,
    dims: tuple[float, float, float],
    shipping_date: str,
) -> list[tuple]:
    """Offers as (airline, total, currency, weight_break) lines, in the order returned."""
    length, width, height = dims
    response = stub.GetQuote(
        quote_pb2.GetQuoteRequest(
            origin=origin,
            destination=destination,
            weight_kg=weight,
            dimensions=quote_pb2.Dimensions(length_cm=length, width_cm=width, height_cm=height),
            shipping_date=shipping_date,
        )
    )
    return [
        (offer.airline, offer.total_price, offer.currency, offer.weight_break)
        for offer in response.offers
    ]


def test_ingest_reports_rows(stub):
    # given the LH sample sheet
    csv_content = (RATE_SHEETS / "LH.csv").read_text()

    # when it is ingested
    rows = ingest(stub, csv_content)

    # then all 4 rows are counted
    assert rows == 4


def test_bulky_shipment_gets_one_offer_per_airline(stub):
    # given all 4 sample sheets
    ingest_samples(stub)

    # when an 80 kg, 120 x 80 x 60 cm shipment (96 kg chargeable) is quoted
    offers = quote(stub, origin="FRA", destination="JFK", weight=80.0,
                   dims=(120.0, 80.0, 60.0), shipping_date="2026-02-10")

    # then each airline quotes the 100 break, sorted by currency and then by price
    assert offers == [
        ("LH", 340.00, "EUR", "100"),
        ("AF", 365.00, "EUR", "100"),
        ("EK", 320.00, "USD", "100"),
        ("QR", 360.00, "USD", "100"),
    ]


def test_well_formed_airport_without_rates_gives_no_offers(stub):
    # given all sample sheets, none of which serves SYD
    ingest_samples(stub)

    # when FRA-SYD is quoted (airports are only checked for format)
    offers = quote(stub, origin="FRA", destination="SYD", weight=80.0,
                   dims=(120.0, 80.0, 60.0), shipping_date="2026-02-10")

    # then the answer is empty, not an error
    assert offers == []


def test_date_outside_every_window_gives_no_offers(stub):
    # given the AF sheet, whose CDG-JFK rows end on 2026-06-30
    ingest(stub, (RATE_SHEETS / "AF.csv").read_text())

    # when CDG-JFK is quoted for 2027-01-01
    offers = quote(stub, origin="CDG", destination="JFK", weight=96.0,
                   dims=(10.0, 10.0, 10.0), shipping_date="2027-01-01")

    # then the answer is empty, not an error
    assert offers == []


def test_malformed_sheet_is_rejected_and_not_stored(stub):
    # given the malformed sample sheet
    csv_content = (RATE_SHEETS / "malformed" / "XX.csv").read_text()

    # when it is ingested
    with pytest.raises(grpc.RpcError) as err:
        ingest(stub, csv_content)

    # then the caller is told why and no XX offer appears
    assert err.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert "missing columns: rate_500" in err.value.details()
    assert quote(stub, origin="FRA", destination="JFK", weight=80.0,
                 dims=(120.0, 80.0, 60.0), shipping_date="2026-02-10") == []


def test_reingesting_an_airline_replaces_its_rates(stub):
    # given all sample sheets, then an LH sheet with only its April-June FRA-JFK row
    ingest_samples(stub)
    header = (RATE_SHEETS / "LH.csv").read_text().splitlines()[0]
    ingest(stub, f"{header}\nLH,FRA,JFK,EUR,2026-04-01,2026-06-30,95.00,4.30,3.95,3.55,3.05,2.70\n")

    # when FRA-JFK is quoted for 2026-02-10
    offers = quote(stub, origin="FRA", destination="JFK", weight=80.0,
                   dims=(120.0, 80.0, 60.0), shipping_date="2026-02-10")

    # then LH has no rate for that date any more and the other airlines are untouched
    assert [offer[0] for offer in offers] == ["AF", "EK", "QR"]


@pytest.mark.parametrize(
    "origin, destination, weight, dims, shipping_date, message",
    [
        ("FRA", "JFK", -10.0, (120.0, 80.0, 60.0), "2026-02-10", "weight must be >= 0"),
        ("FRA", "JFK", 80.0, (120.0, -80.0, 60.0), "2026-02-10", "width must be >= 0"),
        ("FRA", "JFK", 1e26, (120.0, 80.0, 60.0), "2026-02-10", "weight must be <= 100000"),
        ("FRA", "JFK", 80.0, (120.0, 80.0, 60.0), "10/02/2026",
         "shipping_date must be an ISO 8601 date"),
        ("FRANKFURT", "JFK", 80.0, (120.0, 80.0, 60.0), "2026-02-10",
         "invalid origin: 'FRANKFURT'"),
        ("FRA", "jfk", 80.0, (120.0, 80.0, 60.0), "2026-02-10", "invalid destination: 'jfk'"),
    ],
)
def test_invalid_quote_requests(stub, origin, destination, weight, dims, shipping_date, message):
    # given a quote request with one bad field
    # when it is sent
    with pytest.raises(grpc.RpcError) as err:
        quote(stub, origin=origin, destination=destination, weight=weight, dims=dims,
              shipping_date=shipping_date)

    # then the caller gets INVALID_ARGUMENT naming the field
    assert err.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert message in err.value.details()
