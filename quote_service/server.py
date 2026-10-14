"""gRPC entry point. Converts between proto messages and the domain; doubles stop here."""

import logging
from concurrent import futures
from datetime import date
from decimal import Decimal

import grpc

from proto import quote_pb2, quote_pb2_grpc
from quote_service.domain.offer import Offer
from quote_service.domain.shipment import Dimensions, Shipment
from quote_service.errors import InvalidInputError
from quote_service.rates.rate_repository import InMemoryRateRepository
from quote_service.service import QuoteService

log = logging.getLogger(__name__)


class QuoteGrpcService(quote_pb2_grpc.QuoteServiceServicer):
    def __init__(self, service: QuoteService) -> None:
        self._service = service

    def IngestRateSheet(
        self, request: quote_pb2.IngestRateSheetRequest, context: grpc.ServicerContext
    ) -> quote_pb2.IngestRateSheetResponse:
        try:
            rows = self._service.ingest_rate_sheet(request.csv_content)
            return quote_pb2.IngestRateSheetResponse(rows_ingested=rows)
        except InvalidInputError as err:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(err))

    def GetQuote(
        self, request: quote_pb2.GetQuoteRequest, context: grpc.ServicerContext
    ) -> quote_pb2.GetQuoteResponse:
        try:
            offers = self._service.get_quote(to_shipment(request))
            return quote_pb2.GetQuoteResponse(offers=[to_proto_offer(offer) for offer in offers])
        except InvalidInputError as err:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(err))


def to_shipment(request: quote_pb2.GetQuoteRequest) -> Shipment:
    try:
        shipping_date = date.fromisoformat(request.shipping_date)
    except ValueError:
        raise InvalidInputError(
            f"shipping_date must be an ISO 8601 date, e.g. 2026-02-10, got {request.shipping_date!r}"
        ) from None
    return Shipment(
        origin=request.origin,
        destination=request.destination,
        weight_kg=to_decimal(request.weight_kg),
        dimensions=Dimensions(
            length_cm=to_decimal(request.dimensions.length_cm),
            width_cm=to_decimal(request.dimensions.width_cm),
            height_cm=to_decimal(request.dimensions.height_cm),
        ),
        shipping_date=shipping_date,
    )


def to_decimal(value: float) -> Decimal:
    # Through str: Decimal(96.8) would keep the float's binary error, Decimal("96.8") does not.
    return Decimal(str(value))


def to_proto_offer(offer: Offer) -> quote_pb2.Offer:
    return quote_pb2.Offer(
        airline=offer.airline,
        currency=offer.currency,
        chargeable_weight_kg=float(offer.chargeable_weight_kg),
        weight_break=offer.weight_break,
        rate_per_kg=float(offer.rate_per_kg),
        total_price=float(offer.total_price),
    )


def build_server(address: str = "[::]:50051") -> tuple[grpc.Server, int]:
    """Build an unstarted server. Returns it with the port it bound to (useful with port 0)."""
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=8),
        options=[("grpc.so_reuseport", 0)],  # fail loudly if the port is taken
    )
    quote_pb2_grpc.add_QuoteServiceServicer_to_server(
        QuoteGrpcService(QuoteService(InMemoryRateRepository())), server
    )
    port = server.add_insecure_port(address)
    return server, port


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    server, port = build_server()
    server.start()
    log.info("QuoteService listening on port %d", port)
    server.wait_for_termination()


if __name__ == "__main__":
    main()
