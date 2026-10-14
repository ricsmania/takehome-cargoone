"""The two use cases behind the RPCs. Knows storage and rating, not gRPC."""

from decimal import Decimal

from quote_service.domain.airports import is_airport_code
from quote_service.domain.offer import Offer
from quote_service.domain.shipment import Shipment
from quote_service.errors import InvalidInputError
from quote_service.ingestion.csv_rate_sheet import parse_rate_sheet
from quote_service.rating.offers import calculate_offers
from quote_service.storage.rate_repository import RateRepository

# Sanity limits, well above any real air cargo shipment. They keep absurd input from overflowing
# Decimal's precision when chargeable weight is rounded.
MAX_WEIGHT_KG = Decimal(100_000)
MAX_SIDE_CM = Decimal(10_000)


class QuoteService:
    def __init__(self, repository: RateRepository) -> None:
        self._repository = repository

    def ingest_rate_sheet(self, csv_content: str) -> int:
        """Replaces all rates of the sheet's airline. Returns the number of rows stored.

        A sheet holds one airline's rates (README), so the first row names the airline.
        """
        rates = parse_rate_sheet(csv_content)
        self._repository.replace_airline_rates(rates[0].airline, rates)
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
    errors += validate_measure("weight", shipment.weight_kg, MAX_WEIGHT_KG)
    errors += validate_measure("length", shipment.dimensions.length_cm, MAX_SIDE_CM)
    errors += validate_measure("width", shipment.dimensions.width_cm, MAX_SIDE_CM)
    errors += validate_measure("height", shipment.dimensions.height_cm, MAX_SIDE_CM)
    if errors:
        raise InvalidInputError("; ".join(errors))


def validate_measure(name: str, value: Decimal, maximum: Decimal) -> list[str]:
    if not value.is_finite():
        return [f"{name} must be a finite number"]
    if value < 0:
        return [f"{name} must be >= 0"]
    if value > maximum:
        return [f"{name} must be <= {maximum}"]
    return []
