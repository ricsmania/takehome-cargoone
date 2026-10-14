"""Rate sheet parsing: a bad header stops at once, row errors are collected with line numbers."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from quote_service.errors import RateSheetError
from quote_service.ingestion.csv_rate_sheet import parse_rate_sheet

RATE_SHEETS = Path(__file__).parents[3] / "rate_sheets"
HEADER = (
    "airline,origin,destination,currency,valid_from,valid_to,min_charge,"
    "rate_normal,rate_45,rate_100,rate_300,rate_500"
)


def sheet_errors(csv_content: str) -> list[str]:
    with pytest.raises(RateSheetError) as err:
        parse_rate_sheet(csv_content)
    return err.value.errors


@pytest.mark.parametrize("airline, rows", [("LH", 4), ("AF", 3), ("EK", 3), ("QR", 2)])
def test_sample_sheets_parse(airline, rows):
    # given a sample sheet
    csv_content = (RATE_SHEETS / f"{airline}.csv").read_text()

    # when it is parsed
    rates = parse_rate_sheet(csv_content)

    # then every row is kept, all for that airline
    assert len(rates) == rows
    assert {rate.airline for rate in rates} == {airline}


def test_row_values_are_typed():
    # given a row with valid values
    csv_content = f"{HEADER}\nLH,FRA,JFK,EUR,2026-01-01,2026-03-31,90.00,4.10,3.80,3.40,2.95,2.60\n"

    # when it is parsed
    [rate] = parse_rate_sheet(csv_content)

    # then dates are dates and money is Decimal
    assert rate.valid_from == date(2026, 1, 1)
    assert rate.valid_to == date(2026, 3, 31)
    assert rate.min_charge == Decimal("90.00")
    assert rate.rate_45 == Decimal("3.80")


def test_malformed_sample_stops_at_the_header():
    # given rate_sheets/malformed/XX.csv, whose header has no rate_500 column
    csv_content = (RATE_SHEETS / "malformed" / "XX.csv").read_text()

    # when it is parsed
    errors = sheet_errors(csv_content)

    # then only the header error is reported
    assert errors == ["header - missing columns: rate_500"]


def test_malformed_rows_are_reported_with_line_numbers():
    # given the rows of XX.csv with a rate_500 value added, so the header is valid
    csv_content = (
        f"{HEADER}\n"
        "XX,FRA,JFK,EUR,2026-01-01,2026-06-30,90.00,4.10,3.80,3.40,2.95,2.60\n"
        "XX,FRANKFURT,JFK,EUR,2026-01-01,2026-06-30,90.00,4.10,3.80,3.40,2.95,2.60\n"
        "XX,FRA,LHR,EUR,2026-06-30,2026-01-01,90.00,4.10,3.80,3.40,2.95,2.60\n"
        "XX,FRA,CDG,EUR,2026-01-01,2026-06-30,90.00,-4.10,3.80,3.40,2.95,2.60\n"
        "XX,FRA,AMS,EUR,2026-01-01,2026-06-30,90.00,4.10,,3.40,2.95,2.60\n"
    )

    # when it is parsed
    errors = sheet_errors(csv_content)

    # then every bad row is reported, the valid line 2 is not
    assert errors == [
        "line 3 - invalid origin: FRANKFURT",
        "line 4 - valid_to must be >= valid_from",
        "line 5 - rate_normal must be > 0",
        "line 6 - rate_45 is required",
    ]


@pytest.mark.parametrize(
    "row, error",
    [
        (
            "LH,FRA,JFK,GBP,2026-01-01,2026-03-31,90.00,4.10,3.80,3.40,2.95,2.60",
            "unsupported currency: GBP",
        ),
        (
            "LH,FRA,JFK,EUR,2026-13-01,2026-03-31,90.00,4.10,3.80,3.40,2.95,2.60",
            "valid_from must be an ISO 8601 date, got 2026-13-01",
        ),
        (
            "LH,FRA,JFK,EUR,2026-01-01,2026-03-31,90.00,abc,3.80,3.40,2.95,2.60",
            "rate_normal must be > 0",
        ),
        (
            "LH,FRA,JFK,EUR,2026-01-01,2026-03-31,-1,4.10,3.80,3.40,2.95,2.60",
            "min_charge must be >= 0",
        ),
        (
            "Lufthansa,FRA,JFK,EUR,2026-01-01,2026-03-31,90.00,4.10,3.80,3.40,2.95,2.60",
            "invalid airline: Lufthansa",
        ),
        (
            "LH,FRA,JFK,EUR,2026-01-01,2026-03-31,90.00,4.10,3.80,3.40,2.95,2.60,9.99",
            "more values than header columns",
        ),
    ],
)
def test_invalid_row_values(row, error):
    # given a sheet with one bad value on line 2
    csv_content = f"{HEADER}\n{row}\n"

    # when it is parsed
    errors = sheet_errors(csv_content)

    # then the error names the line and the field
    assert errors == [f"line 2 - {error}"]


def test_sheet_without_rows_is_rejected():
    # given a sheet with only a header
    csv_content = f"{HEADER}\n"

    # when it is parsed
    errors = sheet_errors(csv_content)

    # then it is rejected: with no rows there is no airline to replace
    assert errors == ["the sheet has no rate rows"]
