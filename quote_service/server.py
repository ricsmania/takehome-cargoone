"""gRPC entry point. The two RPCs are stubs; the challenge is to fill them in."""

import logging
from concurrent import futures

import grpc

from proto import quote_pb2, quote_pb2_grpc

log = logging.getLogger(__name__)


class QuoteService(quote_pb2_grpc.QuoteServiceServicer):
    def IngestRateSheet(
        self, request: quote_pb2.IngestRateSheetRequest, context: grpc.ServicerContext
    ) -> quote_pb2.IngestRateSheetResponse:
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "IngestRateSheet is yours to build")

    def GetQuote(
        self, request: quote_pb2.GetQuoteRequest, context: grpc.ServicerContext
    ) -> quote_pb2.GetQuoteResponse:
        context.abort(grpc.StatusCode.UNIMPLEMENTED, "GetQuote is yours to build")


def build_server(address: str = "[::]:50051") -> tuple[grpc.Server, int]:
    """Build an unstarted server. Returns it with the port it bound to (useful with port 0)."""
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=8),
        options=[("grpc.so_reuseport", 0)],  # fail loudly if the port is taken
    )
    quote_pb2_grpc.add_QuoteServiceServicer_to_server(QuoteService(), server)
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
