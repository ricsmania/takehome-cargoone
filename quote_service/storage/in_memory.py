"""Keeps rates in memory. Lost on restart; fine for this exercise."""

import threading
from datetime import date

from quote_service.domain.rate import Rate


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
