"""Where rates are stored. Rating never imports this module: the service passes rates in."""

import threading
from typing import Protocol

from quote_service.rate import Rate


class RateRepository(Protocol):
    def replace_airline_rates(self, airline: str, rates: list[Rate]) -> None:
        """Drops every stored rate of the airline and stores these instead."""
        ...

    def get_rates(self, origin: str, destination: str) -> list[Rate]:
        """Every stored rate for the lane, whatever its validity window."""
        ...


class InMemoryRateRepository:
    def __init__(self) -> None:
        self._rates_by_airline: dict[str, list[Rate]] = {}
        self._lock = threading.Lock()  # the gRPC server handles requests on several threads

    def replace_airline_rates(self, airline: str, rates: list[Rate]) -> None:
        with self._lock:
            self._rates_by_airline[airline] = list(rates)

    def get_rates(self, origin: str, destination: str) -> list[Rate]:
        with self._lock:
            all_rates = [rate for rates in self._rates_by_airline.values() for rate in rates]
        return [
            rate for rate in all_rates if rate.origin == origin and rate.destination == destination
        ]
