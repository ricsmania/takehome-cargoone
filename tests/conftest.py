import grpc
import pytest

from proto import quote_pb2_grpc
from quote_service.server import build_server


@pytest.fixture
def stub():
    """A stub talking to a fresh in-process server on a random free port."""
    server, port = build_server("localhost:0")
    server.start()
    with grpc.insecure_channel(f"localhost:{port}") as channel:
        yield quote_pb2_grpc.QuoteServiceStub(channel)
    server.stop(grace=None)
