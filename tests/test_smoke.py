"""Proves the scaffold boots. Replace this file with your own tests."""

import grpc
import pytest

from proto import quote_pb2


def test_get_quote_is_not_implemented_yet(stub):
    # given a booted scaffold with no rating logic
    request = quote_pb2.GetQuoteRequest(origin="FRA", destination="JFK", weight_kg=80)

    # when a quote is requested
    with pytest.raises(grpc.RpcError) as err:
        stub.GetQuote(request)

    # then the server answers UNIMPLEMENTED instead of crashing
    assert err.value.code() == grpc.StatusCode.UNIMPLEMENTED
