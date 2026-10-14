"""Where rates are stored. Rating never imports this module: the service passes rates in."""

import threading
from datetime import date
from typing import Protocol

from quote_service.rate import Rate


class RateRepository(Protocol):
    def replace_airline_rates(self, airline: str, rates: list[Rate]) -> None:
        """Drops every stored rate of the airline and stores these instead."""
        ...

    def get_rates(self, origin: str, destination: str, shipping_date: date) -> list[Rate]:
        """Rates for the lane whose validity window contains shipping_date (both ends inclusive).

        The date is part of the lookup so a database store can filter on it in its query.
        """
        ...


class InMemoryRateRepository:
    def __init__(self) -> None:
        self._rates_by_airline: dict[str, list[Rate]] = {}
        self._lock = threading.Lock()  # the gRPC server handles requests on several threads

    def replace_airline_rates(self, airline: str, rates: list[Rate]) -> None:
        with self._lock:
            self._rates_by_airline[airline] = list(rates)

    def get_rates(self, origin: str, destination: str, shipping_date: date) -> list[Rate]:
        with self._lock:
            all_rates = [rate for rates in self._rates_by_airline.values() for rate in rates]
        return [
            rate
            for rate in all_rates
            if rate.origin == origin
            and rate.destination == destination
            and rate.valid_from <= shipping_date <= rate.valid_to
        ]
