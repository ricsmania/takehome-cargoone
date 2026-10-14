"""The two use cases behind the RPCs. Knows storage and rating, not gRPC."""

from decimal import Decimal

from quote_service.errors import InvalidInputError
from quote_service.pricing import calculate_offers
from quote_service.quote import Offer, Shipment
from quote_service.rate_repository import RateRepository
from quote_service.rate_sheet import parse_rate_sheet
from quote_service.reference_data import is_airport_code


class QuoteService:
    def __init__(self, repository: RateRepository) -> None:
        self._repository = repository

    def ingest_rate_sheet(self, csv_content: str) -> int:
        """Replaces all rates of each airline in the sheet. Returns the number of rows stored."""
        rates = parse_rate_sheet(csv_content)
        for airline in {rate.airline for rate in rates}:
            airline_rates = [rate for rate in rates if rate.airline == airline]
            self._repository.replace_airline_rates(airline, airline_rates)
        return len(rates)

    def get_quote(self, shipment: Shipment) -> list[Offer]:
        validate_shipment(shipment)
        rates = self._repository.get_rates(
            shipment.origin, shipment.destination, shipment.shipping_date
        )
        return calculate_offers(shipment, rates)


def validate_shipment(shipment: Shipment) -> None:
    errors = []
    for field, airport in (("origin", shipment.origin), ("destination", shipment.destination)):
        if not is_airport_code(airport):
            errors.append(f"invalid {field}: {airport!r}")
    errors += validate_non_negative("weight", shipment.weight_kg)
    errors += validate_non_negative("length", shipment.dimensions.length_cm)
    errors += validate_non_negative("width", shipment.dimensions.width_cm)
    errors += validate_non_negative("height", shipment.dimensions.height_cm)
    if errors:
        raise InvalidInputError("; ".join(errors))


def validate_non_negative(name: str, value: Decimal) -> list[str]:
    if not value.is_finite():
        return [f"{name} must be a finite number"]
    if value < 0:
        return [f"{name} must be >= 0"]
    return []
