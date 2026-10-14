"""Parses and validates an airline rate sheet (CSV text). Pure, no I/O."""

import csv
import io
import re
from datetime import date
from decimal import Decimal, InvalidOperation

from quote_service.errors import RateSheetError
from quote_service.rates.rate import Rate
from quote_service.reference_data import CURRENCIES, is_airport_code

RATE_COLUMNS = ["rate_normal", "rate_45", "rate_100", "rate_300", "rate_500"]
COLUMNS = [
    "airline", "origin", "destination", "currency", "valid_from", "valid_to", "min_charge",
    *RATE_COLUMNS,
]
AIRLINE_CODE = re.compile(r"[A-Z0-9]{2}")  # IATA airline designator, e.g. LH


def parse_rate_sheet(csv_content: str) -> list[Rate]:
    """All rows of the sheet, or RateSheetError listing every problem found.

    A bad header stops parsing at once. Row errors are collected and carry their line number.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    missing = [column for column in COLUMNS if column not in (reader.fieldnames or [])]
    if missing:
        raise RateSheetError([f"header - missing columns: {', '.join(missing)}"])

    rates: list[Rate] = []
    errors: list[str] = []
    for row in reader:
        row_errors = validate_row(row)
        if row_errors:
            errors.extend(f"line {reader.line_num} - {error}" for error in row_errors)
        else:
            rates.append(to_rate(row))

    if not rates and not errors:
        errors.append("the sheet has no rate rows")
    if errors:
        raise RateSheetError(errors)
    return rates


def validate_row(row: dict) -> list[str]:
    errors = []
    if None in row:  # DictReader puts values beyond the header under the None key
        errors.append("more values than header columns")

    values = {column: (row.get(column) or "").strip() for column in COLUMNS}
    for column in COLUMNS:
        if not values[column]:
            errors.append(f"{column} is required")

    airline = values["airline"]
    if airline and not AIRLINE_CODE.fullmatch(airline):
        errors.append(f"invalid airline: {airline}")
    for column in ("origin", "destination"):
        if values[column] and not is_airport_code(values[column]):
            errors.append(f"invalid {column}: {values[column]}")
    if values["currency"] and values["currency"] not in CURRENCIES:
        errors.append(f"unsupported currency: {values['currency']}")

    valid_from = parse_date(values["valid_from"])
    valid_to = parse_date(values["valid_to"])
    for column, parsed in (("valid_from", valid_from), ("valid_to", valid_to)):
        if values[column] and parsed is None:
            errors.append(f"{column} must be an ISO 8601 date, got {values[column]}")
    if valid_from and valid_to and valid_to < valid_from:
        errors.append("valid_to must be >= valid_from")

    min_charge = parse_decimal(values["min_charge"])
    if values["min_charge"] and (min_charge is None or min_charge < 0):
        errors.append("min_charge must be >= 0")
    for column in RATE_COLUMNS:
        rate = parse_decimal(values[column])
        if values[column] and (rate is None or rate <= 0):
            errors.append(f"{column} must be > 0")
    return errors


def to_rate(row: dict) -> Rate:
    """Builds a Rate from a row that validate_row accepted."""
    return Rate(
        airline=row["airline"].strip(),
        origin=row["origin"].strip(),
        destination=row["destination"].strip(),
        currency=row["currency"].strip(),
        valid_from=date.fromisoformat(row["valid_from"].strip()),
        valid_to=date.fromisoformat(row["valid_to"].strip()),
        min_charge=Decimal(row["min_charge"].strip()),
        rate_normal=Decimal(row["rate_normal"].strip()),
        rate_45=Decimal(row["rate_45"].strip()),
        rate_100=Decimal(row["rate_100"].strip()),
        rate_300=Decimal(row["rate_300"].strip()),
        rate_500=Decimal(row["rate_500"].strip()),
    )


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_decimal(value: str) -> Decimal | None:
    """None for anything that is not a finite number ("abc", "NaN", "Infinity")."""
    try:
        number = Decimal(value)
    except InvalidOperation:
        return None
    return number if number.is_finite() else None
