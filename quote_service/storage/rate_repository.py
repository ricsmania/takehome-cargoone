"""The storage seam. Rating never imports storage: the service passes rates in."""

from datetime import date
from typing import Protocol

from quote_service.domain.rate import Rate


class RateRepository(Protocol):
    def replace_airline_rates(self, airline: str, rates: list[Rate]) -> None:
        """Drops every stored rate of the airline and stores these instead."""
        ...

    def get_rates(self, origin: str, destination: str, shipping_date: date) -> list[Rate]:
        """Rates for the lane whose validity window contains shipping_date (both ends inclusive).

        The date is part of the lookup so a database store can filter on it in its query.
        """
        ...

